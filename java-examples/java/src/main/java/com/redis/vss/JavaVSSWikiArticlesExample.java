package com.redis.vss;

import redis.clients.jedis.JedisPooled;
import redis.clients.jedis.Protocol;
import redis.clients.jedis.search.Document;
import redis.clients.jedis.search.IndexDefinition;
import redis.clients.jedis.search.IndexOptions;
import redis.clients.jedis.search.Query;
import redis.clients.jedis.search.Schema;
import redis.clients.jedis.search.SearchResult;
import redis.clients.jedis.util.SafeEncoder;

import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Properties;
import java.util.regex.Pattern;
import java.util.stream.Collectors;

import com.opencsv.CSVReader;
import com.opencsv.CSVReaderBuilder;
import com.theokanning.openai.embedding.EmbeddingRequest;
import com.theokanning.openai.service.OpenAiService;

/**
 * Java VSS Wiki Articles Example
 * 
 * @author Michael Yuan
 */

public class JavaVSSWikiArticlesExample {

    // Redis client connection
    private static JedisPooled client = null;

    // OpenAI connection
    private static OpenAiService service = null;

    // Model
    private static String MODEL = "text-embedding-ada-002";
    private static int VECTOR_DIM = 1536; // length of the vectors
    private static int VECTOR_NUMBER = 25000; // initial number of vectors
    private static String INDEX_NAME = "idx_wiki"; // name of the search index
    private static String INDEX_NAME_HNSW = "idx_wiki_hnsw"; // name of the search index
    private static String PREFIX = "wiki"; // prefix for the document keys
    private static String DISTANCE_METRIC = "COSINE"; // prefix for the document keys

    private JavaVSSWikiArticlesExample() {
        try {
            // Initialize Redis connection
            InputStream input = ClassLoader.getSystemResourceAsStream("config.properties");
            Properties prop = new Properties();
            prop.load(input);
            client = new JedisPooled(prop.getProperty("redis.host"),
                    Integer.parseInt(prop.getProperty("redis.port")));

            // Initialize OpenAI service connection

            String token = System.getenv("OPENAI_API_KEY");
            service = new OpenAiService(token);

            // client = new JedisPooled(prop.getProperty("redis.host"),
            // Integer.parseInt(prop.getProperty("redis.port")),
            // prop.getProperty("redis.user"),
            // prop.getProperty("redis.password"));

            Object result = client.sendCommand(Protocol.Command.PING, "Connected to Redis...");
            System.out.println(SafeEncoder.encode((byte[]) result));
        } catch (Exception ex) {
            ex.printStackTrace();
        }
    }

    private void createFlatIndex() {
        try {
            // Drop index if exists
            try {
                client.ftDropIndex(INDEX_NAME);
            } catch (Exception e) {
            }
            ;
            System.out.println("Creating Flat index...");

            HashMap<String, Object> attr = new HashMap<String, Object>();
            attr.put("TYPE", "FLOAT64");
            attr.put("DIM", VECTOR_DIM);
            attr.put("DISTANCE_METRIC", DISTANCE_METRIC);
            attr.put("INITIAL_CAP", VECTOR_NUMBER);

            // Define index schema
            Schema schema = new Schema().addNumericField("id")
                    .addTextField("title", 3.0).as("title")
                    .addTextField("url", 1.0).as("url")
                    .addTextField("text", 2.0).as("text")
                    .addVectorField("title_vector", Schema.VectorField.VectorAlgo.FLAT, attr).as("title_vector")
                    .addVectorField("content_vector", Schema.VectorField.VectorAlgo.FLAT, attr).as("content_vector");
            IndexDefinition rule = new IndexDefinition(IndexDefinition.Type.HASH)
                    .setPrefixes(new String[] { "wiki:" });
            client.ftCreate(INDEX_NAME, IndexOptions.defaultOptions().setDefinition(rule), schema);
        } catch (Exception ex) {
            ex.printStackTrace();
        }
    }

    private void createHNSWIndex() {
        try {
            // Drop index if exists
            try {
                client.ftDropIndex(INDEX_NAME_HNSW);
            } catch (Exception e) {
            }
            ;
            System.out.println("Creating HNSW index...");

            HashMap<String, Object> attr = new HashMap<String, Object>();
            attr.put("TYPE", "FLOAT64");
            attr.put("DIM", VECTOR_DIM);
            attr.put("DISTANCE_METRIC", DISTANCE_METRIC);
            attr.put("INITIAL_CAP", VECTOR_NUMBER);

            // Define index schema
            Schema schema = new Schema().addNumericField("id")
                    .addTextField("title", 3.0).as("title")
                    .addTextField("url", 1.0).as("url")
                    .addTextField("text", 2.0).as("text")
                    .addVectorField("title_vector", Schema.VectorField.VectorAlgo.HNSW, attr).as("title_vector")
                    .addVectorField("content_vector", Schema.VectorField.VectorAlgo.HNSW, attr).as("content_vector");
            IndexDefinition rule = new IndexDefinition(IndexDefinition.Type.HASH)
                    .setPrefixes(new String[] { "wiki:" });
            client.ftCreate(INDEX_NAME_HNSW, IndexOptions.defaultOptions().setDefinition(rule), schema);
        } catch (Exception ex) {
            ex.printStackTrace();
        }
    }

    
    /** 
     * @param csvFile
     * Load data from csv file to Redis hashes
     */
    private void loadData(String csvFile) {
        System.out.println("Loading data in Redis...");
        try {
            FileInputStream input = new FileInputStream(csvFile);
            String[] record = null;
            String key;

            try (CSVReader reader = new CSVReaderBuilder(new InputStreamReader(input)).withSkipLines(1).build()) {
                while ((record = reader.readNext()) != null) {
                    key = PREFIX + ":" + record[0];

                    double[] title_vector = Pattern.compile(", ")
                            .splitAsStream(record[4].replaceAll("\\[", "").replaceAll("\\]", ""))
                            .map(elem -> Double.parseDouble(elem))
                            .collect(Collectors.toList())
                            .stream().mapToDouble(Double::doubleValue).toArray();

                    double[] content_vector = Pattern.compile(", ")
                            .splitAsStream(record[5].replaceAll("\\[", "").replaceAll("\\]", ""))
                            .map(elem -> Double.parseDouble(elem))
                            .collect(Collectors.toList())
                            .stream().mapToDouble(Double::doubleValue).toArray();

                    Map<byte[], byte[]> map = new HashMap<>();
                    map.put("id".getBytes(), record[0].getBytes());
                    map.put("url".getBytes(), record[1].getBytes());
                    map.put("title".getBytes(), record[2].getBytes());
                    map.put("text".getBytes(), record[3].getBytes());
                    map.put("title_vector".getBytes(), doubleToByte(title_vector));
                    map.put("content_vector".getBytes(), doubleToByte(content_vector));
                    map.put("vector_id".getBytes(), record[6].getBytes());

                    client.hset(key.getBytes(), map);
                }
            }

        } catch (Exception ex) {
            ex.printStackTrace();
        }
    }

    
    /** 
     * @param input
     * @return byte[]
     */
    public byte[] doubleToByte(double[] input) {
        ByteBuffer buffer = ByteBuffer.allocate(input.length * Double.BYTES);
        buffer.order(ByteOrder.LITTLE_ENDIAN);
        buffer.asDoubleBuffer().put(input);
        return buffer.array();
    }

    public void searchRedis(String indexName, String queryString, String vector_field, int k) {

        // Build OpenAI embedding request
        EmbeddingRequest embeddingRequest = EmbeddingRequest.builder()
                .model(MODEL)
                .input(Collections.singletonList(queryString))
                .build();

        // Get vector embeddings from Open AI service
        double[] embedding = service.createEmbeddings(embeddingRequest).getData().get(0).getEmbedding()
                .stream().mapToDouble(Double::doubleValue).toArray();

        // Build query
        Query q = new Query("*=>[KNN $k @" + vector_field + "$vec AS vector_score]")
                .setSortBy("vector_score", true)
                .addParam("k", k)
                .addParam("vec", doubleToByte(embedding))
                .limit(0, k)
                .dialect(2);

        // Get and iterate over search results
        SearchResult res = client.ftSearch(indexName, q);
        List<Document> wikis = res.getDocuments();
        int i = 1;
        for (Document wiki : wikis) {
            float score = Float.parseFloat((String) wiki.get("vector_score"));
            System.out.println(i + ". " + wiki.get("title") + " (Score: " + (1 - score) + ")");
            i++;
        }
    }

    /**
     * Run Redis VSS search examples using wiki articles.
     * 
     * @param args The arguments of the program.
     */
    public static void main(String[] args) {

        // Zip archive of wiki articles with OpenAI embeddings
        String fileUrl = "https://cdn.openai.com/API/examples/data/vector_database_wikipedia_articles_embedded.zip";
        String saveAt = "/tmp/vector_database_wikipedia_articles_embedded.zip";
        
        // CSV file of wiki articles with OpenAI embeddings
        String csvFile = "/tmp/vector_database_wikipedia_articles_embedded.csv";
        
        // Download and unzip csv file of wiki articles with OpenAI embeddings
        try {
            System.out.println("Downloading and unzipping csv file...");
            LoadOpenAIData.downloadUsingNIO(fileUrl, saveAt);
            LoadOpenAIData.unzipZip4j(saveAt, "/tmp");

        } catch (IOException e) {
            e.printStackTrace();
        }

        JavaVSSWikiArticlesExample vssArticles = new JavaVSSWikiArticlesExample();
        vssArticles.createFlatIndex();
        vssArticles.createHNSWIndex();
        vssArticles.loadData(csvFile);
       

        System.out.println("### VSS query: 'modern art in Europe' in 'title_vector'");
        vssArticles.searchRedis(INDEX_NAME, "modern art in Europe", "title_vector", 10);

        System.out.println("### VSS query: 'modern art in Europe' in 'title_vector'");
        vssArticles.searchRedis(INDEX_NAME_HNSW, "modern art in Europe", "title_vector", 10);

        System.out.println("### VSS query: 'Famous battles in Scottish history' in 'content_vector'");
        vssArticles.searchRedis(INDEX_NAME, "Famous battles in Scottish history", "content_vector", 10);
    }
}
