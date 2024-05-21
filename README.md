<div align="center">
<div><img src="assets/redis-logo.svg" style="width: 130px"> </div>
<h1>AI Resources</h1>
<div>
    ✨ A curated repository of code recipes, demos, and resources for basic and advanced Redis use cases in the AI ecosystem. ✨
</div>
</div>


## Table of Contents
- Getting started
    - Demos
    - Recipes
- Advanced Capabilities
    - Session memory
    - Semantic cache
    - reranker
- Integrations
- Use cases beyond RAG
    - Recommendation systems
- Additional content
- Benchmarks
- Documentation


# Getting Started

## Demos
The best way to get started is by diving in and playing around with one of our full-featured demos. These Streamlit demos let you toggle different features on and off to find what suits your use case best.

| Demo | Description | Stars |
| --- | --- | --- |
| [⭐ ArxivChatGuru](https://github.com/RedisVentures/ArxivChatGuru) | Streamlit demo of QnA over Arxiv documents with Redis & OpenAI | !
| [Redis VSS - Simple Streamlit Demo](https://github.com/antonum/Redis-VSS-Streamlit) | Streamlit demo of Redis Vector Search |

## Getting started with RAG

Retrieval Augmented Generation (aka RAG) is a system to enhance the ability of an LLM to respond to user queries. The **retrieval** part of RAG is supported by a vector database, which can return semantically relevant results to a user’s query, serving as contextual information to **augment** the **generative** capabilities of an LLM.

To get started with RAG, either from scratch or using a popular framework like Llamaindex or LangChain, see these recipes:

| Recipe | Description |
| --- | --- |
| [/01_redis-py](python-examples/getting_started/01_redis-py.ipynb) | Introduction to vector search using the standard redis python client |
| [/02_redisvl](python-examples/getting_started/02_redisvl.ipynb) | RAG from scratch with the Redis Vector Library |
| [/03_langchain](python-examples/getting_started/03_langchain.ipynb) | RAG using Redis and LangChain |
| [/04_llamaindex](python-examples/getting_started/04_llamaindex.ipynb) | RAG using Redis and LlamaIndex |


# Advanced Capabilities
Often a bare bones implementation is not enough for application needs. If this is the case, the following advanced capabilities are available within RedisVL.

## Semantic Cache
It’s estimated that 31% of LLM queries are potential semantic cache matches ([source](https://arxiv.org/pdf/2403.02694)). Redis, which is most well known for its prowess as a caching layer, can support this in the vector context and help cut down on costly LLM calls that would otherwise be duplicated.

[/semantic_cache](python-examples/advanced_capabilities/semantic_cache.ipynb)


## Session Memory
By default, many LLMs execute statelessly, meaning they respond to queries independently without considering broader conversation or application context. RedisVL allows you to easily add a layer of longer-term memory to assist the LLM in accurately responding to users. This longer-term memory can be configured at the session, application, or user level and is a great way to improve chat performance.

[/session_memory](python-examples/advanced_capabilities/session_memory.ipynb)

## Reranker
Sometimes, the default top K results from a standard vector comparison search to a database are not properly ordered in terms of relevance. When this is the case, using a reranking algorithm can improve which contextual information is utilized by the LLM to respond to a user’s query. Reranking algorithms are more accurate but less speedy than a standard vector search. Used in tandem, reranking serves as the fine-tooth comb to improve the accuracy of vector search while not having to perform costly comparisons over the entire database set.

[/reranker](python-examples/advanced_capabilities/reranker.ipynb)

The diagram below outlines how these pieces might fit into a RAG use case.

# Integrations/Tools
- [⭐ RedisVL](https://github.com/RedisVentures/redisvl) - a dedicated Python client lib for Redis as a Vector DB.
- [⭐ LangChain Python](https://github.com/langchain-ai/langchain) - popular Python client lib for building LLM applications.
powered by Redis.
- [⭐ LangChain JS](https://github.com/langchain-ai/langchainjs) - popular JS client lib for building LLM applications.
powered by Redis.
- [⭐ LlamaIndex](https://gpt-index.readthedocs.io/en/latest/examples/vector_stores/RedisIndexDemo.html) - LlamaIndex Integration for Redis as a vector Database (formerly GPT-index).
- [Semantic Kernel](https://github.com/microsoft/semantic-kernel/tree/main) - popular lib by MSFT to integrate LLMs with plugins.
- [Metal](https://getmetal.io/) - an all-inclusive LLM development platform for building RAG applications. Built on top of Redis as a vector database and high performance data layer.
- [RelevanceAI](https://relevance.ai/) - Platform to ag, search and analyze unstructured data faster, built on Redis.
- [DocArray](https://docarray.jina.ai/advanced/document-store/redis/) - DocArray Integration of Redis as a VectorDB by Jina AI.
- [ChatGPT Memory](https://github.com/continuum-llms/chatgpt-memory) - contextual and adaptive memory for ChatGPT
- [Haystack Example](https://github.com/artefactory/redis-player-one/blob/main/askyves/redis_document_store.py) - Haystack Integration (example) of Redis as a VectorDB.
- [Mantium AI](https://mantiumai.com/)

# Use cases beyond RAG

## Recommendation systems

An exciting example of how Redis can power production-ready systems is highlighted in our collaboration with NVIDIA to construct a state-of-the-art recommendation system.

Within [this repository](https://github.com/redis-developer/redis-nvidia-recsys), you'll find three examples, each escalating in complexity, showcasing the process of building such a system.


# Additional content
- [⭐ NVIDIA Developer Blog -- Offline to Online: Feature Storage for Real Time Recommendation Systems with NVIDIA Merlin](https://developer.nvidia.com/blog/offline-to-online-feature-storage-for-real-time-recommendation-systems-with-nvidia-merlin/)
- [Vector Similarity Search: From Basics to Production](https://mlops.community/vector-similarity-search-from-basics-to-production/) - Introductory blog post to VSS and Redis as a VectorDB.
- [AI-Powered Document Search](https://datasciencedojo.com/blog/ai-powered-document-search/) - Blog post covering AI Powered Document Search Use Cases & Architectures.
- [Vector Search on Azure](https://techcommunity.microsoft.com/t5/azure-developer-community-blog/vector-similarity-search-with-azure-cache-for-redis-enterprise/ba-p/3822059) - Using Azure Redis Enterprise for Vector Search
- [Vector Databases and Large Language Models](https://youtu.be/GJDN8u3Y-T4) - Talk given at LLMs in Production Part 1 by Sam Partee.
- [Vector Databases and AI-powered Search Talk](https://www.youtube.com/watch?v=g2bNHLeKlAg) - Video "Vector Databases and AI-powered Search" given by Sam Partee at SDSC 2023.
- [Engineering Lab Review](https://mlops.community/redis-vector-search-engineering-lab-review/) - Review of the first Redis VSS Hackathon.
- [Real-Time Product Recommendations](https://jina.ai/news/real-time-product-recommendation-using-redis-and-docarray/) - Content-based recsys design with Redis and DocArray.
- [Redis as a Vector Database](https://vishnudeva.medium.com/redis-as-a-vector-database-rediscloud-2a444c478f3d) - Hackathon review blog post covering Redis as a VectorDB.
- [LabLab AI Redis Tech Page](https://lablab.ai/tech/redis)
- [Storing and querying for embeddings with Redis](https://blog.baeke.info/2023/03/21/storing-and-querying-for-embeddings-with-redis/)
- [Building Intelligent Apps with Redis Vector Similarity Search](https://redis.com/blog/build-intelligent-apps-redis-vector-similarity-search/)
- [Rediscovering Redis for Vector Similarity](https://redis.com/blog/rediscover-redis-for-vector-similarity-search/)
- [VSS Cheat Sheet](https://drive.google.com/file/d/10O52YXE1-x9jUTv2G-iJUHFSbthWAcyy/view?usp=share_link) - Redis Vector Search Cheat Sheet by Datascience Dojo.
- [RedisDays Keynote](https://www.youtube.com/watch?v=EEIBTEpb2LI) - Video "Infuse Real-Time AI Into Your "Financial Services" Application".
- [RedisDays Trading Signals](https://www.youtube.com/watch?v=_Lrbesg4DhY) - Video "Using AI to Reveal Trading Signals Buried in Corporate Filings".
- [LLM Stack Hackathon writeup](https://medium.com/@sonam.gupta1105/equipping-with-llm-stack-mlops-community-hackathon-fd0505762c85) - Building a QnA Slack bot for the MLOps Community Hackathon with OpenAI and Redis

# Benchmarks
- [Vector Database Benchmarks](https://jina.ai/news/benchmark-vector-search-databases-with-one-million-data/) - Jina AI VectorDB benchmarks comparing Redis against others.
- [ANN Benchmarks](https://ann-benchmarks.com) - Standard ANN Benchmarks site. *Only using single Redis OSS instance/client.*

# Documentation
- [Redis Vector Database QuickStart](https://redis.io/docs/get-started/vector-database/)
- [Redis Vector Similarity Docs](https://redis.io/docs/interact/search-and-query/advanced-concepts/vectors/) - Official Redis literature for Vector Similarity Search.
- [Redis-py Search Docs](https://redis.readthedocs.io/en/latest/redismodules.html#redisearch-commands) - Redis-py client library docs for RediSearch.
- [Redis-py General Docs](https://redis.readthedocs.io/en/latest/) - Redis-py client library documentation.
- [Redis Stack](https://redis.io/docs/stack/) - Redis Stack documentation.
- [Redis Clients](https://redis.io/docs/clients/) - Redis client list.
