<div align="center">
<div><img src="../assets/redis-logo.svg" style="width: 130px"> </div>
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

[**Setup**](#setup) | [**Running the Project**](#running-the-project) | [**Notebooks**](#notebooks) | [**Project Structure**](#project-structure) | [**Implementation Details**](#implementation-details)

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

| Notebook | Description |
| --- | --- |
| [RAG/spring_ai_redis_rag.ipynb](./RAG/spring_ai_redis_rag.ipynb) | Demonstrates building a RAG-based beer recommendation chatbot using Spring AI and Redis as the vector store |

## Project Structure

```bash
java-recipes/
├── .env                         # Environment variables (create this)
├── docker-compose.yml           # Docker Compose configuration
├── jupyter/                     # Jupyter configuration files
│   ├── Dockerfile               # Dockerfile for Jupyter with Java kernel
│   ├── environment.yml          # Conda environment specification
│   ├── install.py               # JJava kernel installation script
│   ├── kernel.json              # Kernel specification
│   └── java/                    # Java dependencies and configuration
│       └── pom.xml              # Maven project file with dependencies
└── resources/                   # Data files for notebooks
    └── beers.json.gz            # Compressed beer dataset
```

## Implementation Details

### Java Jupyter Kernel

The project uses [JJava](https://github.com/dflib/jjava), a Jupyter kernel for Java based on JShell. This allows for interactive Java development in Jupyter notebooks.

Key components:

- Java 21 for modern Java features
- Maven for dependency management
- JJava kernel for Jupyter integration

### Spring AI Integration

The Spring AI notebooks showcase how to use Spring's AI capabilities with Redis:

- **Spring AI**: Framework for building AI-powered applications
- **Redis Vector Store**: Used for storing and querying vector embeddings
- **Transformer Models**: For generating embeddings locally
- **RAG Pattern**: Demonstrates the Retrieval Augmented Generation pattern

### Docker Configuration

The Docker setup includes:

1. **Jupyter Container**:
   - Based on minimal Jupyter notebook image
   - Adds Java 21, Maven, and the JJava kernel
   - Includes Python environment with PyTorch and other ML libraries

2. **Redis Container**:
   - Uses Redis Stack image with Vector Search capabilities
   - Persists data using Docker volumes
   - Exposes Redis on port 6379 and RedisInsight on port 8001

## Example Applications

### Beer Recommendation Chatbot

The `spring-ai-rag.ipynb` notebook demonstrates:

- Loading and embedding beer data into Redis Vector Store
- Using local transformer models for generating embeddings
- Connecting to OpenAI for LLM capabilities
- Building a RAG pipeline to answer beer-related queries
- Semantic search over beer properties and descriptions
