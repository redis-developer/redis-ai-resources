<div align="center">
<div><img src="../assets/redis-logo.svg" style="width: 130px" alt=""> </div>
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

[**Notebooks**](#notebooks) | [**Applications**](#applications) | [**Example Applications**](#example-notebooks--applications)

</div>
<br>

There are two types of Java Recipes: Notebooks and Applications. Notebooks are interactive, self-contained examples in Jupyter format that let you explore AI concepts step by step that mix code, explanations, and output in one place. Applications, on the other hand, are full Spring Boot projects meant for building real-world systems. They show how to structure, run, and scale actual AI-powered apps using Redis, embedding models, and Spring AI in a production-like setup.

## Notebooks

Notebooks require a Jupyter Notebook environment to run. Check out the [Setup Instructions & Implementation Details](./notebooks/README.md) for more details on how to set up your environment.

| Notebook                                                                             | Description                                                                                                  |
|--------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------|
| [notebooks/RAG/spring_ai_redis_rag.ipynb](./notebooks/RAG/spring_ai_redis_rag.ipynb) | Demonstrates building a RAG-ba sed beer recommendation chatbot using Spring AI and Redis as the vector store |

## Applications

| Application                                                                                                                                     | Description                                                                                                 |
|-------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------|
| [applications/agent-memory](./applications/agent-memory/spring_boot_agent_memory.md)                                                            | Demonstrates how to implement short-term and long-term memory for AI agents using Redis vector capabilities |
| [applications/vector-similarity-search/redis-om-spring](./applications/vector-similarity-search/redis-om-spring/spring_boot_redis_om_spring.md) | Demonstrates building a vector similarity search application using Spring Boot and Redis OM Spring          |
| [applications/vector-similarity-search/spring-ai](./applications/vector-similarity-search/spring-ai/spring_boot_spring_ai.md)                   | Demonstrates building a vector similarity search application using Spring Boot and Spring AI                |

