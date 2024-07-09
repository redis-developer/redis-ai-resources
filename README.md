<div align="center">
<div><img src="assets/redis-logo.svg" style="width: 130px"> </div>
<h1>AI Resources</h1>
<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
![Language](https://img.shields.io/github/languages/top/redis-developer/redis-ai-resources)
![GitHub last commit](https://img.shields.io/github/last-commit/redis-developer/redis-ai-resources)

</div>
<div>
    ✨ A curated repository of code recipes, demos, and resources for basic and advanced Redis use cases in the AI ecosystem. ✨
</div>

<div></div>


<br>
</div>

# Table of Contents
- [Demos](#Demos)
- [Recipes](#Recipes)
    - [RAG](#getting-started-with-rag)
    - [Semantic cache](#semantic-cache)
    - [Advanced RAG](#advanced-rag)
    - [Recommendation systems](#recommendation-systems)
- [Integrations](#integrations)
- [Additional content](#additional-content)
- [Benchmarks](#benchmarks)
- [Documentation](#documentation)

<br>

# Demos
No faster way to get started than by diving in and playing around with one of our demos.

| Demo | Description |
| --- | --- |
| [ArxivChatGuru](https://github.com/redis-developer/ArxivChatGuru) | Streamlit demo of RAG over Arxiv documents with Redis & OpenAI |
| [Redis VSS - Simple Streamlit Demo](https://github.com/antonum/Redis-VSS-Streamlit) | Streamlit demo of Redis Vector Search |
| [Vertex AI & Redis](https://github.com/redis-developer/gcp-redis-llm-stack/tree/main) | A tutorial featuring Redis with Vertex AI |
| [Agentic RAG](https://github.com/redis-developer/agentic-rag) | A tutorial focused on agentic RAG with LlamaIndex and Cohere |
| [ArXiv Search](https://github.com/redis-developer/redis-arxiv-search) | Full stack implementation of Redis with React FE |
| [Product Search](https://github.com/redis-developer/redis-product-search) |  Vector search with Redis Stack and Redis Enterprise |

# Recipes

Need specific sample code to help get started with Redis? Start here.

## Getting started with Redis & Vector Search

| Recipe | Description |
| --- | --- |
| [/redis-intro/redis_intro.ipynb](python-recipes/redis-intro/redis_intro.ipynb) | The place to start if brand new to Redis |
| [/vector-search/00_redispy.ipynb](python-recipes/vector-search/00_redispy.ipynb) | Vector search with Redis python client |
| [/vector-search/01_redisvl.ipynb](python-recipes/vector-search/01_redisvl.ipynb) | Vector search with Redis Vector Library |

## Getting started with RAG

**Retrieval Augmented Generation** (aka RAG) is a technique to enhance the ability of an LLM to respond to user queries. The **retrieval** part of RAG is supported by a vector database, which can return semantically relevant results to a user’s query, serving as contextual information to **augment** the **generative** capabilities of an LLM.

To get started with RAG, either from scratch or using a popular framework like Llamaindex or LangChain, go with these recipes:

| Recipe | Description |
| --- | --- |
| [/RAG/01_redisvl.ipynb](python-recipes/RAG/01_redisvl.ipynb) | RAG from scratch with the Redis Vector Library |
| [/RAG/02_langchain.ipynb](python-recipes/RAG/02_langchain.ipynb) | RAG using Redis and LangChain |
| [/RAG/03_llamaindex.ipynb](python-recipes/RAG/03_llamaindex.ipynb) | RAG using Redis and LlamaIndex |
| [/RAG/04_advanced_redisvl.ipynb](python-recipes/RAG/04_advanced_redisvl.ipynb) | Advanced RAG with redisvl |
| [/RAG/05_nvidia_ai_rag_redis.ipynb](python-recipes/RAG/05_nvidia_ai_rag_redis.ipynb) | RAG using Redis and Nvidia |
| [/RAG/06_ragas_evaluation.ipynb](python-recipes/RAG/06_ragas_evaluation.ipynb) | Utilize RAGAS  framework to evaluate RAG performance |


## Semantic Cache
An estimated 31% of LLM queries are potentially redundant ([source](https://arxiv.org/pdf/2403.02694)). Redis enables semantic caching to help cut down on LLM costs quickly.

| Recipe | Description |
| --- | --- |
| [/semantic-cache/semantic_caching_gemini.ipynb](python-recipes/semantic-cache/semantic_caching_gemini.ipynb) | Build a semantic cache with Redis and Google Gemini |

## Advanced RAG
For further insights on enhancing RAG applications with dense content representations, query re-writing, and other techniques.

| Recipe | Description |
| --- | --- |
[/RAG/04_advanced_redisvl.ipynb](python-recipes/RAG/04_advanced_redisvl.ipynb) | Notebook for additional tips and techniques to improve RAG quality |

## Recommendation systems

An exciting example of how Redis can power production-ready systems is highlighted in our collaboration with [NVIDIA](https://developer.nvidia.com/blog/offline-to-online-feature-storage-for-real-time-recommendation-systems-with-nvidia-merlin/) to construct a state-of-the-art recommendation system.

Within [this repository](https://github.com/redis-developer/redis-nvidia-recsys), you'll find three examples, each escalating in complexity, showcasing the process of building such a system.


# Integrations/Tools
- [⭐ RedisVL](https://github.com/redis/redis-vl-python) - a dedicated Python client lib for Redis as a Vector DB.
- [⭐ AWS Bedrock](https://redis.io/docs/latest/integrate/amazon-bedrock/) - Streamlines GenAI deployment by offering foundational models as a unified API.
- [⭐ LangChain Python](https://github.com/langchain-ai/langchain) - popular Python client lib for building LLM applications.
powered by Redis.
- [⭐ LangChain JS](https://github.com/langchain-ai/langchainjs) - popular JS client lib for building LLM applications.
powered by Redis.
- [⭐ LlamaIndex](https://gpt-index.readthedocs.io/en/latest/examples/vector_stores/RedisIndexDemo.html) - LlamaIndex Integration for Redis as a vector Database (formerly GPT-index).
- [Semantic Kernel](https://github.com/microsoft/semantic-kernel/tree/main) - popular lib by MSFT to integrate LLMs with plugins.
- [RelevanceAI](https://relevance.ai/) - Platform to ag, search and analyze unstructured data faster, built on Redis.
- [DocArray](https://docs.docarray.org/user_guide/storing/index_redis/) - DocArray Integration of Redis as a VectorDB by Jina AI.


# Additional content
- [Vector Similarity Search: From Basics to Production](https://mlops.community/vector-similarity-search-from-basics-to-production/) - Introductory blog post to VSS and Redis as a VectorDB.
- [AI-Powered Document Search](https://datasciencedojo.com/blog/ai-powered-document-search/) - Blog post covering AI Powered Document Search Use Cases & Architectures.
- [Vector Search on Azure](https://techcommunity.microsoft.com/t5/azure-developer-community-blog/vector-similarity-search-with-azure-cache-for-redis-enterprise/ba-p/3822059) - Using Azure Redis Enterprise for Vector Search
- [Vector Databases and Large Language Models](https://youtu.be/GJDN8u3Y-T4) - Talk given at LLMs in Production Part 1 by Sam Partee.
- [Vector Databases and AI-powered Search Talk](https://www.youtube.com/watch?v=g2bNHLeKlAg) - Video "Vector Databases and AI-powered Search" given by Sam Partee at SDSC 2023.
- [Engineering Lab Review](https://mlops.community/redis-vector-search-engineering-lab-review/) - Review of the first Redis VSS Hackathon.
- [Real-Time Product Recommendations](https://jina.ai/news/real-time-product-recommendation-using-redis-and-docarray/) - Content-based recsys design with Redis and DocArray.
- [LabLab AI Redis Tech Page](https://lablab.ai/tech/redis)
- [Storing and querying for embeddings with Redis](https://blog.baeke.info/2023/03/21/storing-and-querying-for-embeddings-with-redis/)
- [Building Intelligent Apps with Redis Vector Similarity Search](https://redis.com/blog/build-intelligent-apps-redis-vector-similarity-search/)
- [RedisDays Keynote](https://www.youtube.com/watch?v=EEIBTEpb2LI) - Video "Infuse Real-Time AI Into Your "Financial Services" Application".
- [RedisDays Trading Signals](https://www.youtube.com/watch?v=_Lrbesg4DhY) - Video "Using AI to Reveal Trading Signals Buried in Corporate Filings".

# Benchmarks
- [Benchmarking results for vector databases](https://redis.io/blog/benchmarking-results-for-vector-databases/) - Benchmarking results for vector databases, including Redis and 7 other Vector Database players.
- [ANN Benchmarks](https://ann-benchmarks.com) - Standard ANN Benchmarks site. *Only using single Redis OSS instance/client.*

# Documentation
- [Redis Vector Database QuickStart](https://redis.io/docs/get-started/vector-database/)
- [Redis Vector Similarity Docs](https://redis.io/docs/interact/search-and-query/advanced-concepts/vectors/) - Official Redis literature for Vector Similarity Search.
- [Redis-py Search Docs](https://redis.readthedocs.io/en/latest/redismodules.html#redisearch-commands) - Redis-py client library docs for RediSearch.
- [Redis-py General Docs](https://redis.readthedocs.io/en/latest/) - Redis-py client library documentation.
- [Redis Stack](https://redis.io/docs/stack/) - Redis Stack documentation.
- [Redis Clients](https://redis.io/docs/clients/) - Redis client list.
