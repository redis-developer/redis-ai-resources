# Vector Search with Redis OM Spring (SpringBoot)

Vector similarity search (also known as semantic search) is a powerful technique that allows you to find items based on their semantic meaning rather than exact keyword matches. Redis Query Engine supports vector similarity search through its vector indexing capabilities, enabling you to implement semantic search applications with high performance and low latency.

This demo showcases how to implement vector similarity search using Redis OM Spring, a library that simplifies working with Redis data models and the Redis Query Engine.

## Learning resources:

- Article: [Semantic Search with Spring Boot & Redis](https://raphaeldelio.com/2025/04/29/semantic-search-with-spring-boot-redis/)
- Video: [Autocomplete in Spring with Redis](https://www.youtube.com/watch?v=rjaR1PR5gVk)
- Video: [What is an embedding model?](https://youtu.be/0U1S0WSsPuE)
- Video: [Exact vs Approximate Nearest Neighbors - What's the difference?](https://youtu.be/9NvO-VdjY80)
- Video: [What is semantic search?](https://youtu.be/o3XN4dImESE)
- Video: [What is a vector database?](https://youtu.be/Yhv19le0sBw)


## Repository

The repository for this demo can be found [here](https://github.com/redis-developer/redis-springboot-resources/tree/main/search/vector-search)

## Requirements

To run this demo, you’ll need the following installed on your system:
- Docker – [Install Docker](https://docs.docker.com/get-docker/)
- Docker Compose – Included with Docker Desktop or available via CLI installation guide

## Running the demo

The easiest way to run the demo is with Docker Compose, which sets up all required services in one command.

### Step 1: Clone the repository

If you haven’t already:

```bash
git clone https://github.com/redis-developer/redis-springboot-recipes.git
cd redis-springboot-recipes/search/full-text-search-and-autocomplete
```

### Step 2: Start the services

```bash
docker compose up --build
```

This will start:

- redis: for storing documents
- redis-insight: a UI to explore the Redis data
- vector-search-app: the Spring Boot app that implements vector search

## Using the demo

When all of your services are up and running. Go to `localhost:8080` to access the demo.

If you search using the extract box, the system will perform semantic search and find items on the database that are semantically similar to your query:

![Screenshot of a movie search app using vector similarity search. The user searches for “movie about a clownfish who searches for his son.” The top result is Finding Nemo, with a similarity score of 0.505, followed by Big Fish and Swordfish. Each result includes a poster, title, year, cast, genres, and description snippet.](readme-assets/vector-search.png)

You can also apply filters for pre-filtering the results before applying semantic search:

![Screenshot of a movie search app using vector similarity search with filters applied: cast = Albert Brooks, genre = animated. The query is “movie about a clownfish who searches for his son.” Results include Finding Nemo, Finding Nemo 3D, and Finding Dory, each with similarity scores, posters, cast, genres, and descriptions.](readme-assets/pre-filtered-vector-search.png)

This demo also supports autocompletion of the title:

![Close-up screenshot of a movie search app’s autocomplete feature. The user types “Finding” in the “Movie Title” field, triggering a dropdown with suggestions like Finding You, Finding Nemo, Finding Dory, Finding Bliss, and Finding Amanda. Autocomplete response time is shown as 8 ms.](readme-assets/autocomplete.png)

### Redis Insight

RedisInsight is a graphical tool developed by Redis to help developers and administrators interact with and manage Redis databases more efficiently. It provides a visual interface for exploring keys, running commands, analyzing memory usage, and monitoring performance metrics in real-time. RedisInsight supports features like full-text search, time series, streams, and vector data structures, making it especially useful for working with more advanced Redis use cases. With its intuitive UI, it simplifies debugging, optimizing queries, and understanding data patterns without requiring deep familiarity with the Redis CLI.

The Docker Compose file will also spin up an instance of Redis Insight. We can access it by going to `localhost:5540`:

If we go to Redis Insight, we will be able to see the data stored in Redis:

![Screenshot of RedisInsight showing 10,000 JSON movie documents in the com.redis.vectorsearch.domain.Movie namespace. The selected document is for Star Trek III: The Search for Spock, displaying fields like title, year, genres, extract, and a thumbnail URL. The embeddedExtract vector field is also included.](readme-assets/redis-insight.png)

And if run the command `FT.INFO 'com.redis.fulltextsearchandautocomplete.domain.MovieIdx'`, we'll be able to see the schema that was created for indexing our documents efficiently:

![Screenshot of RedisInsight displaying the schema of the MovieIdx vector search index. The index is built on JSON documents and includes fields like title, year, cast, genres, embeddedExtract (VECTOR), and id. The vector field uses the HNSW algorithm with FLOAT32 data type, 384 dimensions, COSINE distance metric, M=16, and EF_CONSTRUCTION=200.](readme-assets/index-redis-insight.png)

## How It Is Implemented

The application uses Redis OM Spring to vectorize documents and perform vector similarity search. Here's how it works:

### Defining Vector Fields with Redis OM Spring Annotations

Documents are defined as Java classes with Redis OM Spring annotations that specify how they should be vectorized and indexed:

```java
@Document
public class Movie {
    // Other fields...

    @Vectorize(
            destination = "embeddedExtract",
            embeddingType = EmbeddingType.SENTENCE
    )
    private String extract;

    @Indexed(
            schemaFieldType = SchemaFieldType.VECTOR,
            algorithm = VectorField.VectorAlgorithm.HNSW,
            type = VectorType.FLOAT32,
            dimension = 384,
            distanceMetric = DistanceMetric.COSINE,
            initialCapacity = 10
    )
    private float[] embeddedExtract;

    // Getters and setters...
}
```

Let's break down the annotations:

- `@Vectorize`: Automatically generates vector embeddings for the text field
   - `destination`: Specifies the field where the embedding will be stored
   - `embeddingType`: Defines the granularity of the embedding (SENTENCE in this case)

- `@Indexed` with vector parameters:
   - `schemaFieldType = SchemaFieldType.VECTOR`: Marks this as a vector field
   - `algorithm = VectorField.VectorAlgorithm.HNSW`: Uses the Hierarchical Navigable Small World algorithm for efficient approximate nearest neighbor search
   - `type = VectorType.FLOAT32`: Specifies the vector data type
   - `dimension = 384`: Sets the vector dimension (must match the number of dimensions output by the embedding model)
   - `distanceMetric = DistanceMetric.COSINE`: Uses cosine similarity for distance calculation

### Storing and Vectorizing Documents

When documents are saved to Redis using the repository, Redis OM Spring automatically generates vector embeddings:

```java
public void loadAndSaveMovies(String filePath) throws Exception {
    // Load movies from JSON file
    List<Movie> movies = objectMapper.readValue(is, new TypeReference<>() {});

    // Save movies in batches
    int batchSize = 500;
    for (int i = 0; i < unprocessedMovies.size(); i += batchSize) {
        int end = Math.min(i + batchSize, unprocessedMovies.size());
        List<Movie> batch = unprocessedMovies.subList(i, end);
        movieRepository.saveAll(batch);
    }
}
```

When `movieRepository.saveAll(batch)` is called:
1. Redis OM Spring generates vector embeddings for the `extract` field
2. The embeddings are stored in the `embeddedExtract` field
3. The documents are saved to Redis with their vector embeddings
4. Redis creates a vector index for efficient similarity search

### Performing Vector Similarity Search

Vector similarity search is implemented using Redis OM Spring's EntityStream API:

```java
public Map<String, Object> search(
        String title,
        String extract,
        List<String> actors,
        Integer year,
        List<String> genres,
        Integer numberOfNearestNeighbors
) {
    SearchStream<Movie> stream = entityStream.of(Movie.class);

    if (extract != null) {
        // Convert search query to vector embedding
        float[] embeddedQuery = embedder.getTextEmbeddingsAsFloats(List.of(extract), Movie$.EXTRACT).getFirst();

        // Perform KNN search with the embedded query
        stream = stream.filter(Movie$.EMBEDDED_EXTRACT.knn(numberOfNearestNeighbors, embeddedQuery))
                        .sorted(Movie$._EMBEDDED_EXTRACT_SCORE);
    }

    // Apply additional filters
    List<Pair<Movie, Double>> matchedMovies = stream
            .filter(Movie$.TITLE.containing(title))
            .filter(Movie$.CAST.eq(actors))
            .filter(Movie$.YEAR.eq(year))
            .filter(Movie$.GENRES.eq(genres))
            .map(Fields.of(Movie$._THIS, Movie$._EMBEDDED_EXTRACT_SCORE))
            .collect(Collectors.toList());

    return result;
}
```

This method:
1. Converts the search query text into a vector embedding using the same embedding model
2. Performs a K-Nearest Neighbors (KNN) search to find the most similar vectors
3. Applies additional filters to narrow down the results (pre-filtering)
4. Returns the matched movies along with their similarity scores

### Combining Vector Search with Autocomplete

The application also supports autocomplete functionality alongside vector search:

```java
public interface MovieRepository extends RedisDocumentRepository<Movie, String> {
    List<Suggestion> autoCompleteTitle(String title, AutoCompleteOptions options);
}
```

The `autoCompleteTitle` method is automatically implemented by Redis OM Spring based on the `@AutoComplete` annotation on the `title` field in the Movie class.

### How Redis Indexes the Vectors

When the application starts, Redis OM Spring creates a vector index in Redis based on the annotations:

```
FT.CREATE idx:com.redis.vectorsearch.domain.Movie ON JSON PREFIX 1 com.redis.vectorsearch.domain.Movie: SCHEMA 
    $.title AS title TEXT SORTABLE 
    $.year AS year NUMERIC SORTABLE 
    $.cast AS cast TAG 
    $.genres AS genres TAG 
    $.embeddedExtract AS embeddedExtract VECTOR HNSW 6 TYPE FLOAT32 DIM 384 DISTANCE_METRIC COSINE INITIAL_CAP 10
```

This index enables efficient vector similarity search with the following features:
- HNSW algorithm for approximate nearest neighbor search
- 384-dimensional FLOAT32 vectors
- Cosine similarity as the distance metric
- Additional text and tag fields for filtering

This approach allows for high-performance semantic search operations, even with large datasets, by leveraging Redis's in-memory data structures and the Redis Query Engine's vector search capabilities.
