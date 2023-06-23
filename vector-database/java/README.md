# Redis VSS OpenAI Examples in Java

## Contents
1.  [Summary](#summary)
2.  [Features](#features)
3.  [Prerequisites](#prerequisites)
4.  [Installation](#installation)
5.  [Usage](#usage)
6.  [Execution](#execution)

## Summary <a name="summary"></a>
This provides a series of Java code examples of how to use Redis VSS with vector embeddings generated with OpenAI.

## Features <a name="features"></a>
- Java source code for implementing Redis VSS on JSON documents using an ecommerce dataset of products and obtaining vector embeddings from OpenAI.
- Java source code for implementing Redis VSS on Redis Hashes using a dataset with wikipedia articles with OpenAI vector embeddings.
- Docker compose file to start up a Redis Stack instance.

## Prerequisites <a name="prerequisites"></a>
- Docker
- Java JDK
- [OpenAI key](https://platform.openai.com)

## Installation <a name="installation"></a>
1.  Clone this repo.
2.  CD to the java directory
3.  Export an environment variable with your OpenAI API key: ```export OPENAI_API_KEY="<YOUR_KEY>"```
4.  Start up Redis Stack:  docker compose up -d
5.  Using a JDK or Java IDE build the maven project and run the examples

## Execution <a name="execution"></a>
### Redis Client Connection 
 ```java
client = new JedisPooled(prop.getProperty("redis.host"),
                    Integer.parseInt(prop.getProperty("redis.port")));
 ```
 ### OpenAI Client Connection
 ```java
service = new OpenAiService(token);
 ```
 ### Flat Index Build
 ```java
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
 ```
 ### HNSW Index Build
 ```java
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
```
### Redis Hash Data Load
```java
Map<byte[], byte[]> map = new HashMap<>();
map.put("id".getBytes(), record[0].getBytes());
map.put("url".getBytes(), record[1].getBytes());
map.put("title".getBytes(), record[2].getBytes());
map.put("text".getBytes(), record[3].getBytes());
map.put("title_vector".getBytes(), doubleToByte(title_vector));
map.put("content_vector".getBytes(), doubleToByte(content_vector));
map.put("vector_id".getBytes(), record[6].getBytes());
client.hset(key.getBytes(), map);
```
### Redis JSON Data Load
```java
Product product = productList.get(i);
product.addVector(embeddings.get(i).getEmbedding().stream().mapToDouble(Double::doubleValue)
    .toArray());
client.jsonSet("product:" + product.id, gson.toJson(product));
```
### VSS query: 'modern art in Europe' in 'title_vector'
```text
1. Museum of Modern Art (Score: 0.8751771)
2. Western Europe (Score: 0.8674411)
3. Renaissance art (Score: 0.86415625)
4. Pop art (Score: 0.8603469)
5. Northern Europe (Score: 0.85465807)
6. Hellenistic art (Score: 0.8527923)
7. Modernist literature (Score: 0.84703135)
8. Art film (Score: 0.84327316)
9. Central Europe (Score: 0.84258366)
10. European (Score: 0.84141064)
```
### VSS query: 'Famous battles in Scottish history' in 'content_vector'
```text
1. Battle of Bannockburn (Score: 0.86933625)
2. Wars of Scottish Independence (Score: 0.8614707)
3. 1651 (Score: 0.85258836)
4. First War of Scottish Independence (Score: 0.84962213)
5. Robert I of Scotland (Score: 0.84621406)
6. 841 (Score: 0.84399074)
7. 1716 (Score: 0.84390485)
8. 1314 (Score: 0.83721495)
9. 1263 (Score: 0.8364166)
10. William Wallace (Score: 0.83534056)
```
### VSS query: 'man blue jeans' in 'productVector'
```text
1. John Players Men Blue Jeans (Score: 0.79446274)
2. Lee Men Tino Blue Jeans (Score: 0.7797863)
3. Lee Men Blue Chicago Fit Jeans (Score: 0.77107173)
4. Lee Men Blue Chicago Fit Jeans (Score: 0.7710503)
5. Peter England Men Party Blue Jeans (Score: 0.7699358)
6. Locomotive Men Washed Blue Jeans (Score: 0.74747217)
7. Locomotive Men Washed Blue Jeans (Score: 0.74747217)
8. French Connection Men Blue Jeans (Score: 0.7463001)
9. Palm Tree Kids Boy Washed Blue Jeans (Score: 0.7440362)
10. Lee Men Elvira Rinse Blue Chicago Fit Jeans (Score: 0.7366651)
```
### VSS query: 'man blue jeans' in 'productVector' with hybrid filters: @productDisplayName:"slim fit"
```text
1. Lee Rinse Navy Blue Slim Fit Jeans (Score: 0.71524847)
2. Basics Men Blue Slim Fit Checked Shirt (Score: 0.71524143)
3. Basics Men Blue Slim Fit Checked Shirt (Score: 0.71524143)
4. Tokyo Talkies Women Navy Slim Fit Jeans (Score: 0.6794758)
5. Basics Men Navy Slim Fit Checked Shirt (Score: 0.6708832)
6. Basics Men Red Slim Fit Checked Shirt (Score: 0.6275975)
7. Basics Men White Slim Fit Striped Shirt (Score: 0.622632)
8. ADIDAS Men's Slim Fit White T-shirt (Score: 0.5857945)
```
### VSS query: 'man blue jeans' in 'productVector' with hybrid filters: (@year:[2011 2012] @season:{Summer})
```text
1. John Players Men Blue Jeans (Score: 0.79437006)
2. Peter England Men Party Blue Jeans (Score: 0.7699023)
3. French Connection Men Blue Jeans (Score: 0.746287)
4. Denizen Women Blue Jeans (Score: 0.7350321)
5. Do U Speak Green Men Blue Shorts (Score: 0.7293731)
6. John Players Men Check Blue Shirt (Score: 0.7255274)
7. Jealous 21 Women Washed Blue Jeans (Score: 0.7209517)
8. Jealous 21 Women Washed Blue Jeans (Score: 0.7209517)
9. Lee Men Solid Blue Shirts (Score: 0.7166283)
10. Gini and Jony Boys Check Blue Shirt (Score: 0.7127073)
```