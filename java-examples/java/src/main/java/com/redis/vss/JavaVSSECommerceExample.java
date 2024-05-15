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

import java.io.InputStream;
import java.io.InputStreamReader;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Properties;

import com.google.gson.Gson;
import com.opencsv.CSVReader;
import com.opencsv.CSVReaderBuilder;
import com.theokanning.openai.embedding.EmbeddingRequest;
import com.theokanning.openai.embedding.Embedding;
import com.theokanning.openai.service.OpenAiService;

/**
 * Java VSS ECommerce Example
 * 
 * @author Michael Yuan
 */
public class JavaVSSECommerceExample {

    // Redis client connection
    private static JedisPooled client = null;

    // OpenAI connection
    private static OpenAiService service = null;

    // Model
    private static String MODEL = "text-embedding-ada-002";
    private static int VECTOR_DIM = 1536; // length of the vectors
    private static String INDEX_NAME = "idx_prod"; // name of the search index
    private static String PREFIX = "product"; // prefix for the document keys
    private static String DISTANCE_METRIC = "L2"; // prefix for the document keys

    // Product POJO to be converted to JSON doc
    private class Product {
        private int id;
        private String gender;
        private String season;
        private String masterCategory;
        private String subCategory;
        private String articleType;
        private String baseColour;
        private int year;
        private String usage;
        private String productDisplayName;
        private double[] productVector;

        public Product(int id, String gender, String season, String masterCategory, String subCategory,
                String articleType, String baseColour, int year, String usage, String productDisplayName) {
            this.id = id;
            this.gender = gender;
            this.season = season;
            this.masterCategory = masterCategory;
            this.subCategory = subCategory;
            this.articleType = articleType;
            this.baseColour = baseColour;
            this.year = year;
            this.usage = usage;
            this.productDisplayName = productDisplayName;
        }

        public void addVector(double[] vector) {
            this.productVector = vector;
        }
    }

    private JavaVSSECommerceExample() {
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

            Object result = client.sendCommand(Protocol.Command.PING, "HELLO! Connected to Redis.");
            System.out.println(SafeEncoder.encode((byte[]) result));
        } catch (Exception ex) {
            ex.printStackTrace();
        }
    }

    private void createIndex() {
        try {
            // Drop index if exists
            try {
                client.ftDropIndex(INDEX_NAME);
            } catch (Exception e) {
            };
            System.out.println("Creating index...");

            HashMap<String, Object> attr = new HashMap<String, Object>();
            attr.put("TYPE", "FLOAT64");
            attr.put("DIM", VECTOR_DIM);
            attr.put("DISTANCE_METRIC", DISTANCE_METRIC);

            // Define index schema
            Schema schema = new Schema().addNumericField("$.id")
                    .addTagField("$.gender").as("gender")
                    .addTagField("$.season").as("season")
                    .addTextField("$.masterCategory", 1.0).as("masterCategory")
                    .addTextField("$.subCategory", 1.0).as("subCategory")
                    .addTextField("$.articleType", 1.0).as("articleType")
                    .addTextField("$.baseColour", 1.0).as("baseColour")
                    .addNumericField("$.year").as("year")
                    .addTextField("$.usage", 1.0).as("usage")
                    .addTextField("$.productDisplayName", 1.0).as("productDisplayName")
                    .addVectorField("$.productVector", Schema.VectorField.VectorAlgo.FLAT, attr).as("productVector");
            IndexDefinition rule = new IndexDefinition(IndexDefinition.Type.JSON)
                    .setPrefixes(new String[] { PREFIX + ":" });

            // Create Index        
            client.ftCreate(INDEX_NAME, IndexOptions.defaultOptions().setDefinition(rule), schema);
        } catch (Exception ex) {
            ex.printStackTrace();
        }
    }
    
    // Load data from csv file to Redis JSON documents
    private void loadData() {
        System.out.println("Loading data...");
        try {
            InputStream input = ClassLoader.getSystemResourceAsStream("styles_2k.csv");
            String[] record = null;
            String productText = null;
            List<String> productTextList = new ArrayList<String>();
            List<Product> productList = new ArrayList<Product>();
            Gson gson = new Gson();
            int counter = 0;
            int batchsize = 1000; // Embeddings batch size

            // Read CSV file
            try (CSVReader reader = new CSVReaderBuilder(new InputStreamReader(input)).withSkipLines(1).build()) {
                while ((record = reader.readNext()) != null) {
                    
                    // create Product POJO from csv records
                    Product prod = new Product(Integer.parseInt(record[0]), record[1], record[6], record[2], record[3],
                            record[4], record[5], Integer.parseInt(record[7]), record[8], record[9]);

                    // create product text to be used for OpenAI vector embeddings
                    productText = "name " + record[9].toLowerCase() + " category " + record[3].toLowerCase() +
                            " subcategory " + record[4].toLowerCase() + " color " + record[5].toLowerCase() + " gender "
                            + record[1].toLowerCase();

                    // list with Product POJOs
                    productList.add(counter, prod);

                    // list with product text for batch request to OpenAI
                    productTextList.add(counter, productText);

                    // Batch requests to OpenAI to generate embeddings for products
                    if (counter % batchsize == 0) {
                        List<Embedding> embeddings = embeddingsBatchRequest(productTextList);
                        for (int i = 0; i < productList.size(); i++) {
                            Product product = productList.get(i);
                            product.addVector(embeddings.get(i).getEmbedding().stream().mapToDouble(Double::doubleValue)
                                    .toArray());
                            client.jsonSet("product:" + product.id, gson.toJson(product));
                        }
                        counter = 0;
                    }
                    counter++;
                }
                List<Embedding> embeddings = embeddingsBatchRequest(productTextList);
                for (int i = 0; i < productList.size(); i++) {
                    Product product = productList.get(i);
                    product.addVector(
                            embeddings.get(i).getEmbedding().stream().mapToDouble(Double::doubleValue).toArray());
                    client.jsonSet("product:" + product.id, gson.toJson(product));
                }
            }
        } catch (Exception ex) {
            ex.printStackTrace();
        }
    }

    
    /** 
     * OpenAI batch requests to generate vector embeddings
     * 
     * @param productTextList
     * @return List<Embedding>
     */
    private List<Embedding> embeddingsBatchRequest(List<String> productTextList) {

        EmbeddingRequest embeddingRequest = EmbeddingRequest.builder()
                .model(MODEL)
                .input(productTextList)
                .build();

        List<Embedding> embeddings = service.createEmbeddings(embeddingRequest).getData();

        return embeddings;
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

    
    /** 
     * @param indexName
     * @param queryString
     * @param hybridFields
     * @param vectorField
     * @param k
     */
    public void searchRedis(String indexName, String queryString, String hybridFields, String vectorField, int k) {

        // Fields that will be returned from query results
        String[] returnFields = new String[] { "id", "gender", "season", "masterCategory", 
                "subCategory","articleType","baseColour", "year", "usage", "productDisplayName", "vector_score" };

        // Creates embedding vector from user query
        EmbeddingRequest embeddingRequest = EmbeddingRequest.builder()
                .model(MODEL)
                .input(Collections.singletonList(queryString))
                .build();

        double[] embedding = service.createEmbeddings(embeddingRequest).getData().get(0).getEmbedding()
                .stream().mapToDouble(Double::doubleValue).toArray();

        // Build query
        Query q = new Query(hybridFields + "=>[KNN $k @" + vectorField + "$vec AS vector_score]")
                .returnFields(returnFields)
                .setSortBy("vector_score", true)
                .addParam("k", k)
                .addParam("vec", doubleToByte(embedding))
                .limit(0, k)
                .dialect(2);

        // Get and iterate over query results
        SearchResult res = client.ftSearch(indexName, q);
        List<Document> products = res.getDocuments();
        int i = 1;
        for (Document prod : products) {
            float score = Float.parseFloat((String) prod.get("vector_score"));
            System.out.println(i + ". " + prod.get("productDisplayName") + " (Score: " + (1 - score) + ")");
            i++;
        }
    }

    /**
     * Run Redis VSS search examples using ecommerce product data.
     * 
     * @param args The arguments of the program.
     */
    public static void main(String[] args) {

        JavaVSSECommerceExample vssEcommerce = new JavaVSSECommerceExample();
        vssEcommerce.createIndex();
        vssEcommerce.loadData();

        System.out.println("### VSS query: 'man blue jeans' in 'productVector'");
        vssEcommerce.searchRedis(INDEX_NAME,"man blue jeans", "*", "productVector", 10);

        System.out.println("### VSS query: 'man blue jeans' in 'productVector' with hybrid filters: @productDisplayName:\"slim fit\"");
        vssEcommerce.searchRedis(INDEX_NAME,"man blue jeans", "@productDisplayName:\"slim fit\"", "productVector", 10);

        System.out.println("### VSS query: 'man blue jeans' in 'productVector' with hybrid filters: (@year:[2011 2012] @season:{Summer})");
        vssEcommerce.searchRedis(INDEX_NAME,"man blue jeans", "(@year:[2011 2012] @season:{Summer})", "productVector", 10);

    }
}
