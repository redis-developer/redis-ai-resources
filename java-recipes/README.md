<div align="center">
<div><img src="../../assets/redis-logo.svg" style="width: 130px"> </div>
<h1>Redis AI Java Resources</h1>
<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
![Java](https://img.shields.io/badge/Java-21-orange)
![Spring AI](https://img.shields.io/badge/Spring%20AI-1.0.0--M6-green)

</div>
<div>
    ✨ Java-based code examples, notebooks, and resources for using Redis in AI and ML applications. ✨
</div>

<div></div>
<br>

[**Notebooks**](#notebooks) | [**Applications**](#applications) | [**Example Applications**](#example-applications)

</div>
<br>

## Setup

This project uses Docker Compose to set up a complete environment for running Java-based AI applications with Redis. The environment includes:

- A Jupyter Notebook server with Java kernel support
- Redis Stack (includes Redis and RedisInsight)
- Pre-installed dependencies for AI/ML workloads

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/)
- OpenAI API key (for notebooks that use OpenAI services)

### Environment Configuration

1. Create a `.env` file in the project root with your OpenAI API key:

```bash
OPENAI_API_KEY=your_openai_api_key_here
```

## Running the Project

1. Clone the repository (if you haven't already):

   ```bash
   git clone https://github.com/redis-developer/redis-ai-resources.git
   cd redis-ai-resources/java-recipes
   ```

2. Start the Docker containers:

   ```bash
   docker-compose up -d
   ```

3. Access the Jupyter environment:
   - Open your browser and navigate to [http://localhost:8888](http://localhost:8888)
   - The token is usually shown in the docker-compose logs. You can view them with:

     ```bash
     docker-compose logs jupyter
     ```

4. Access RedisInsight:
   - Open your browser and navigate to [http://localhost:8001](http://localhost:8001)
   - Connect to Redis using the following details:
     - Host: redis-java
     - Port: 6379
     - No password (unless configured)

5. When finished, stop the containers:

   ```bash
   docker-compose down
   ```

## Notebooks

| Notebook                                                                             | Description                                                                                                  |
|--------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------|
| [notebooks/RAG/spring_ai_redis_rag.ipynb](./notebooks/RAG/spring_ai_redis_rag.ipynb) | Demonstrates building a RAG-ba sed beer recommendation chatbot using Spring AI and Redis as the vector store |

## Applications

| Application                                                                                                                 | Description                                                                                        |
|-----------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------|
| [applications/vector-similarity-search/spring_boot](./applications/vector-similarity-search/spring_boot_redis_om_spring.md) | Demonstrates building a vector similarity search application using Spring Boot and Redis OM Spring |


## Example Notebooks & Applications

### Beer Recommendation Chatbot

The `spring-ai-rag.ipynb` notebook demonstrates:

- Loading and embedding beer data into Redis Vector Store
- Using local transformer models for generating embeddings
- Connecting to OpenAI for LLM capabilities
- Building a RAG pipeline to answer beer-related queries
- Semantic search over beer properties and descriptions

### Vector Similarity Search with Redis OM Spring and Spring Boot

The `spring_boot_redis_om_spring` directory contains a Spring Boot application that demonstrates how to use Redis OM Spring for vector similarity search. The application allows you to:
- Add movies to the Redis database
- Search for movies based on semantic similarity on the synopsis of the movie
- Perform hybrid search by adding filters to genre, cast, and year 

