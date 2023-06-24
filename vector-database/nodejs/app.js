/**
 * @fileoverview Redis VSS w/AI integration examples
 * 
 */

import { createClient, SchemaFieldTypes, VectorAlgorithms } from 'redis';
import * as dotenv from 'dotenv';
import { Configuration, OpenAIApi } from 'openai';
import fsPromises from 'node:fs/promises';

/**
 * Creates a Redis client connection and executes the ping command on it.
 * @returns {_RedisClientType}
 */
async function redisClient() {
    const client = createClient({url: 'redis://localhost:6379'});
    await client.connect();
    const result = await client.ping();
    console.log('*** Redis Connection ***')
    console.log(result);
    return client;
}

/**
 * Submits a prompt to ChatGPT and returns the response
 * @param {OpenAIApi} openai
 * @param {string} prompt
 * @param {string} model
 * @returns {Promise<string>} 
 */
async function getCompletion(openai, prompt, model="gpt-3.5-turbo") {
    const msg = [{"role": "user", "content": prompt}]
    const response = await openai.createChatCompletion({
        model: model,
        messages: msg,
        temperature: 0
    });
    return response.data.choices[0].message.content;
}

/**
 * Submits text to ChatGPT and returns its embedding (array of floats)
 * @param {OpenAIApi} openai
 * @param {string} content
 * @returns {Promise<float[]>}  
 */
async function getEmbedding(openai, content) {
    const response = await openai.createEmbedding({
        model: 'text-embedding-ada-002',
        input: content
    });
    return response.data.data[0].embedding;
}

/**
 * Opens an OpenAI connection and pings for response
 * @returns {Promise<OpenAIApi>} 
 */
async function openaiClient() {
    const config = new Configuration({apiKey: process.env.OPENAI_API_KEY,});
    const client = new OpenAIApi(config);
    const response = await getCompletion(client, 'ping');
    console.log('\n*** OpenAI Connection ***')
    console.log(response);
    return client;
}

/**
 * Builds 2 different indices in Redis, each with a vector and text field.  One index is on vectors stored in
 * JSON objects; the other is on vectors stored in hashsets.
 * @param {_RedisClientType} redis
 * @returns {Promise<void>}
 */
async function buildIndices(redis) {
    try {
        await redis.ft.dropIndex('idx1');
        await redis.ft.dropIndex('idx2');
    } 
    catch(err) {};

    const idx1 = await redis.ft.create('idx1', {
        '$.vector': {
            type: SchemaFieldTypes.VECTOR,
            AS: 'vector',
            ALGORITHM: VectorAlgorithms.FLAT,
            TYPE: 'FLOAT32',
            DIM: 1536,
            DISTANCE_METRIC: 'L2'
        },
        '$.content': {
            type: SchemaFieldTypes.TEXT,
            AS: 'content'
        }
    }, { ON: 'JSON', PREFIX: 'jsonDoc:'});
    
    const idx2 = await redis.ft.create('idx2', {
        'vector': {
            type: SchemaFieldTypes.VECTOR,
            ALGORITHM: VectorAlgorithms.HNSW,
            TYPE: 'FLOAT32',
            DIM: 1536,
            M: 48,
            DISTANCE_METRIC: 'COSINE'
        },
        'content': {
            type: SchemaFieldTypes.TEXT,
        }
    }, { ON: 'HASH', PREFIX: 'hashDoc:'});

    console.log('\n*** Indices Build ***');
    console.log(`idx1 (FLAT, L2, 1536, FLOAT32, JSON): ${idx1}`);
    console.log(`idx2 (HNSW, COSINE, 1536, FLOAT32, M=48, HASH): ${idx2}`);
}

/**
 * Loads text files into hash and JSON objects in Redis.  The text of each file is vectorized and stored in that hash or
 * JSON.
 * @param {_RedisClientType} redis
 * @param {OpenAIApi} openai
 * @returns {Promise<void>}
 */
async function loadData(redis, openai) {
    let files = await fsPromises.readdir('./data');
    files = files.filter(file => file.endsWith(('.txt')));
    let i = 0;

    for (const file of files) {
        let content = await fsPromises.readFile(`./data/${file}`, { encoding: 'utf8' });
        content = content.replace(/[\r\n]/gm, " ");
        const vector = await getEmbedding(openai, content);

        await redis.json.set(`jsonDoc:${i}`, '$', { "content": content, "vector": vector });
        await redis.hSet(`hashDoc:${i}`, { content: content, vector: Buffer.from(new Float32Array(vector).buffer) });
        i++;
    }

    console.log('\n*** Data Load ***');
    console.log(`Number of JSON documents loaded: ${i}`);
    console.log(`Number of HASH documents loaded: ${i}`);
}

/**
 * Executes 2 different VSS scenarios using 2 different index and object types.
 * @param {_RedisClientType} redis
 * @param {OpenAIApi} openai
 * @returns {Promise<void>}
 */
async function vectorSearch(redis, openai) {
    //Vector search scenario #1
    let topic = "Teenager LaShawn Merritt ran the third fastest indoor 400m of all time at the Fayetteville Invitational meeting."
    let vector = await getEmbedding(openai, topic);
    let result = await redis.ft.search('idx1', '*=>[KNN 2 @vector $query_vec]', {
        PARAMS: { query_vec: Buffer.from(new Float32Array(vector).buffer) },
        DIALECT: 2,
        SORTBY: {
            BY: '__vector_score',
            DIRECTIION: 'ASC'
        }
    });
    console.log('\n*** Vector Search #1 ***');
    console.log('Scenario:  JSON docs, FLAT index, Top 2 KNN, Sports topic input');
    for (const doc of result.documents) {
        console.log(`\nkey: ${doc.id}`);
        console.log(`content: ${doc.value.content}`);
    }

    // Vector search scenario #2
    topic = "The History Boys by Alan Bennett has been named best new play in the Critics' Circle Theatre Awards."
    vector = await getEmbedding(openai, topic);
    result = await redis.ft.search('idx2', '(@content:"Christian Slater")=>[KNN 2 @vector $query_vec]', {
        PARAMS: { query_vec: Buffer.from(new Float32Array(vector).buffer) },
        DIALECT: 2,
        SORTBY: {
            BY: '__vector_score',
            DIRECTIION: 'ASC'
        }
    });
    console.log('\n*** Vector Search #2 ***');
    console.log('Scenario:  HASH docs, HNSW index, Hybrid w/Top 2 KNN, Entertainment topic input');
    for (const doc of result.documents) {
        console.log(`\nkey: ${doc.id}`);
        console.log(`content: ${doc.value.content}`);
    }
}

/**
 * Executes a ChatGPT prompt on data that is outside of ChatGPT knowledge cut-off date.  Then, the prompt is vectorized
 * and Redis is search for relevant documents that provide context.  The ChatGTP prompt is then re-executed with that 
 * additional context.
 * @param {_RedisClientType} redis
 * @param {OpenAIApi} openai
 * @returns {Promise<void>}
 */
async function qna(redis, openai) {
    let prompt = "Is Sam Bankman-Fried's company, FTX, considered a well-managed company?";

    console.log('\n*** AI Q&A #1 ***')
    console.log('Scenario:  Ask the AI a question which is outside of its knowledge base');
    console.log(`Prompt: ${prompt}`);
    console.log(`Response: ${await getCompletion(openai, prompt)}`);

    console.log('\n*** AI Q&A #2 ***')
    console.log('Scenario:  Vectorize the question, search Redis for relevant docs, then provide additional info from Redis to the AI');
    const vector = await getEmbedding(openai, prompt);
    const result = await redis.ft.search('idx1', '*=>[KNN 1 @vector $query_vec]', {
        PARAMS: { query_vec: Buffer.from(new Float32Array(vector).buffer) },
        DIALECT: 2,
        SORTBY: {
            BY: '__vector_score',
            DIRECTIION: 'ASC'
        }
    });
    prompt = `Using the information delimited by triple hyphens, answer this question: Is Sam Bankman-Fried's company, FTX, considered a well-managed company?

    Context: ---${result.documents[0].value.content}---`
    console.log(`Prompt: ${prompt}`);
    console.log(`\nResponse: ${await getCompletion(openai, prompt)}`);
}

/**
 * Main function that executes all the functions above.
 */
(async () => {
    dotenv.config();
    const redis = await redisClient();
    const openai = await openaiClient();   
    await buildIndices(redis);
    await loadData(redis, openai);
    await vectorSearch(redis, openai);
    await qna(redis, openai);
    await redis.disconnect();
})();