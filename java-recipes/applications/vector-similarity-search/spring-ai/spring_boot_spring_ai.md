# Vector Search with Spring AI (SpringBoot)

Vector similarity search (semantic search) allows you to find items based on their semantic meaning rather than exact keyword matches. Spring AI provides a standardized way to work with AI models and vector embeddings across different providers. This demo showcases how to integrate Redis Vector Search with Spring AI to implement semantic search applications.

## Learning resources:

- Article: [Semantic Search with Spring Boot & Redis](https://raphaeldelio.com/2025/04/29/semantic-search-with-spring-boot-redis/)
- Video: [What is an embedding model?](https://youtu.be/0U1S0WSsPuE)
- Video: [What is semantic search?](https://youtu.be/o3XN4dImESE)
- Video: [What is a vector database?](https://youtu.be/Yhv19le0sBw)

## Repository

The repository for this demo can be found [here](https://github.com/redis-developer/redis-springboot-resources/tree/main/search/vector-search-spring-ai)

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
- vector-search-spring-ai-app: the Spring Boot app that implements vector search

## Using the demo

When all of your services are up and running. Go to `localhost:8080` to access the demo.

If you search using the extract box, the system will perform semantic search and find items on the database that are semantically similar to your query:

![Screenshot of a movie search app using vector similarity search. The user searches for “movie about a clownfish who searches for his son.” The top result is Finding Nemo, with a similarity score of 0.505, followed by Big Fish and Swordfish. Each result includes a poster, title, year, cast, genres, and description snippet.](readme-assets/vector-search.png)

You can also apply filters for pre-filtering the results before applying semantic search:

![Screenshot of a movie search app using vector similarity search with filters applied: cast = Albert Brooks, genre = animated. The query is “movie about a clownfish who searches for his son.” Results include Finding Nemo, Finding Nemo 3D, and Finding Dory, each with similarity scores, posters, cast, genres, and descriptions.](readme-assets/pre-filtered-vector-search.png)

### Redis Insight

RedisInsight is a graphical tool developed by Redis to help developers and administrators interact with and manage Redis databases more efficiently. It provides a visual interface for exploring keys, running commands, analyzing memory usage, and monitoring performance metrics in real-time. RedisInsight supports features like full-text search, time series, streams, and vector data structures, making it especially useful for working with more advanced Redis use cases. With its intuitive UI, it simplifies debugging, optimizing queries, and understanding data patterns without requiring deep familiarity with the Redis CLI.

The Docker Compose file will also spin up an instance of Redis Insight. We can access it by going to `localhost:5540`:

If we go to Redis Insight, we will be able to see the data stored in Redis:

![Screenshot of RedisInsight showing 10,000 JSON movie documents in the com.redis.vectorsearch.domain.Movie namespace. The selected document is for Star Trek III: The Search for Spock, displaying fields like title, year, genres, extract, and a thumbnail URL. The embeddedExtract vector field is also included.](readme-assets/redis-insight.png)

And if run the command `FT.INFO 'com.redis.fulltextsearchandautocomplete.domain.MovieIdx'`, we'll be able to see the schema that was created for indexing our documents efficiently:

![Screenshot of RedisInsight displaying the schema of the MovieIdx vector search index. The index is built on JSON documents and includes fields like title, year, cast, genres, embeddedExtract (VECTOR), and id. The vector field uses the HNSW algorithm with FLOAT32 data type, 384 dimensions, COSINE distance metric, M=16, and EF_CONSTRUCTION=200.](readme-assets/index-redis-insight.png)

## How It Is Implemented

The application uses Spring AI's `RedisVectorStore` to store and search vector embeddings of movie descriptions.

### Configuring the Vector Store

```kotlin
@Bean
fun movieVectorStore(
    embeddingModel: EmbeddingModel,
    jedisPooled: JedisPooled
): RedisVectorStore {
    return RedisVectorStore.builder(jedisPooled, embeddingModel)
        .indexName("movieIdx")
        .contentFieldName("extract")
        .embeddingFieldName("extractEmbedding")
        .metadataFields(
            RedisVectorStore.MetadataField("title", Schema.FieldType.TEXT),
            RedisVectorStore.MetadataField("year", Schema.FieldType.NUMERIC),
            RedisVectorStore.MetadataField("cast", Schema.FieldType.TAG),
            RedisVectorStore.MetadataField("genres", Schema.FieldType.TAG),
            RedisVectorStore.MetadataField("thumbnail", Schema.FieldType.TEXT),
        )
        .prefix("movies:")
        .initializeSchema(true)
        .vectorAlgorithm(RedisVectorStore.Algorithm.HSNW)
        .build()
}
```

Let's break this down:

- **Index Name**: `movieIdx` - Redis will create an index with this name for searching movies
- **Content Field**: `extract` - The movie description that will be embedded
- **Embedding Field**: `extractEmbedding` - The field that will store the resulting vector embedding
- **Metadata Fields**: Additional fields for filtering and retrieval (title, year, cast, genres, thumbnail)
- **Prefix**: `movies:` - All keys in Redis will be prefixed with this to organize the data
- **Vector Algorithm**: `HSNW` - Hierarchical Navigable Small World algorithm for efficient approximate nearest neighbor search

### Configuring the Embedding Model

Spring AI provides a standardized way to work with different embedding models. In this application, we use the Transformers embedding model:

```kotlin
@Bean
fun embeddingModel(): EmbeddingModel {
    return TransformersEmbeddingModel()
}
```

The `TransformersEmbeddingModel` is a local embedding model based on the Hugging Face Transformers library, which allows us to generate vector embeddings without relying on external API calls.

### Storing and Vectorizing Documents

When the application starts, it loads movie data from a JSON file and stores it in Redis with vector embeddings:

```kotlin
fun storeMovies(movies: List<Movie>) {
    val documents = movies.map { movie ->
        val text = movie.extract ?: ""
        val metadata = mapOf(
            "title" to (movie.title ?: ""),
            "year" to movie.year,
            "cast" to movie.cast,
            "genres" to movie.genres,
            "thumbnail" to (movie.thumbnail ?: "")
        )
        Document(text, metadata)
    }
    movieVectorStore.add(documents)
}
```

This process:
1. Converts each Movie object to a Spring AI Document
2. Sets the movie extract as the document content
3. Adds metadata fields for filtering and retrieval
4. Adds the documents to the RedisVectorStore, which automatically:
  - Generates vector embeddings for the content
  - Stores the documents in Redis with their embeddings
  - Updates the vector index for efficient search

### Performing Vector Similarity Search

When a user enters a search query, the application performs vector similarity search to find semantically similar movies:

```kotlin
fun searchMovies(
    title: String,
    extract: String,
    actors: List<String>,
    year: Int? = null,
    genres: List<String>,
    numberOfNearestNeighbors: Int
): Map<String, Any> {
    val b = FilterExpressionBuilder()
    val filterList = mutableListOf<FilterExpressionBuilder.Op>()

    // Add filters for title, actors, year, and genres
    if (title.isNotBlank()) {
        filterList.add(b.`in`("title", title))
    }

    // ... other filters ...

    val filterExpression = when (filterList.size) {
        0 -> null
        1 -> filterList[0]
        else -> filterList.reduce { acc, expr -> b.and(acc, expr) }
    }?.build()

    val searchResults = movieVectorStore.similaritySearch(
        SearchRequest.builder()
            .query(extract)
            .topK(numberOfNearestNeighbors)
            .filterExpression(filterExpression)
            .build()
    ) ?: emptyList()

    // Transform results to Movie objects
    // ...
}
```

This search process:
1. Builds filter expressions for pre-filtering based on metadata (title, actors, year, genres)
2. Creates a search request with:
  - The extract text as the query (which will be embedded into a vector)
  - A topK parameter to limit the number of results
  - Optional filter expressions for pre-filtering
3. Performs vector similarity search using the RedisVectorStore
4. Transforms the search results back into Movie objects with similarity scores

### Pre-filtering with Vector Search

One powerful feature of Redis vector search is the ability to pre-filter results before performing vector similarity search. This allows for more efficient and targeted searches:

```kotlin
val filterExpression = when (filterList.size) {
    0 -> null
    1 -> filterList[0]
    else -> filterList.reduce { acc, expr -> b.and(acc, expr) }
}?.build()

val searchResults = movieVectorStore.similaritySearch(
    SearchRequest.builder()
        .query(extract)
        .topK(numberOfNearestNeighbors)
        .filterExpression(filterExpression)
        .build()
)
```

Pre-filtering works by:
1. First applying traditional filters on metadata fields (e.g., year, cast, genres)
2. Then performing vector similarity search only on the filtered subset
3. Returning the top K most similar results from the filtered set

This approach combines the precision of traditional filtering with the semantic understanding of vector search, allowing users to find movies that are both semantically similar to their query and match specific criteria.
