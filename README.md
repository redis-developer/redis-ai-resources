<div align="center">
<div><img src="assets/redis-logo.svg" style="width: 130px"> </div>
<h1>AI Resources</h1>
<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
![Language](https://img.shields.io/github/languages/top/redis-developer/redis-ai-resources)
![GitHub last commit](https://img.shields.io/github/last-commit/redis-developer/redis-ai-resources)



</div>
<div>
    ✨ A curated repository of code recipes, demos, tutorials and resources for basic and advanced Redis use cases in the AI ecosystem. ✨
</div>

<div></div>
<br>

[**Demos**](#demos) | [**Recipes**](#recipes) | [**Tutorials**](#tutorials) | [**Integrations**](#integrations) | [**Content**](#content) | [**Benchmarks**](#benchmarks) | [**Docs**](#docs)

</div>
<br>

## Demos
No faster way to get started than by diving in and playing around with a demo.

| Demo | Description |
| --- | --- |
| [Redis RAG Workbench](https://github.com/redis-developer/redis-rag-workbench) | Interactive demo to build a RAG-based chatbot over a user-uploaded PDF. Toggle different settings and configurations to improve chatbot performance and quality. Utilizes RedisVL, LangChain, RAGAs, and more. |
| [Redis VSS - Simple Streamlit Demo](https://github.com/antonum/Redis-VSS-Streamlit) | Streamlit demo of Redis Vector Search |
| [ArXiv Search](https://github.com/redis-developer/redis-arxiv-search) | Full stack implementation of Redis with React FE |
| [Product Search](https://github.com/redis-developer/redis-product-search) |  Vector search with Redis Stack and Redis Enterprise |
| [ArxivChatGuru](https://github.com/redis-developer/ArxivChatGuru) | Streamlit demo of RAG over Arxiv documents with Redis & OpenAI |


## Recipes

Need quickstarts to begin your Redis AI journey? **Start here.**

### Getting started with Redis & Vector Search

| Recipe | Description |
| --- | --- |
| [/redis-intro/00_redis_intro.ipynb](/python-recipes/redis-intro/00_redis_intro.ipynb) | The place to start if brand new to Redis |
| [/vector-search/00_redispy.ipynb](/python-recipes/vector-search/00_redispy.ipynb) | Vector search with Redis python client |
| [/vector-search/01_redisvl.ipynb](/python-recipes/vector-search/01_redisvl.ipynb) | Vector search with Redis Vector Library |
| [/vector-search/02_hybrid_search.ipynb](/python-recipes/vector-search/02_hybrid_search.ipynb) | Hybrid search techniques with Redis (BM25 + Vector) |
| [/vector-search/03_float16_support.ipynb](/python-recipes/vector-search/03_float16_support.ipynb) | Shows how to convert a float32 index to use float16 |


### Retrieval Augmented Generation (RAG)

**Retrieval Augmented Generation** (aka RAG) is a technique to enhance the ability of an LLM to respond to user queries. The **retrieval** part of RAG is supported by a vector database, which can return semantically relevant results to a user’s query, serving as contextual information to **augment** the **generative** capabilities of an LLM.

To get started with RAG, either from scratch or using a popular framework like Llamaindex or LangChain, go with these recipes:

| Recipe | Description |
| --- | --- |
| [/RAG/01_redisvl.ipynb](python-recipes/RAG/01_redisvl.ipynb) | RAG from scratch with the Redis Vector Library |
| [/RAG/02_langchain.ipynb](python-recipes/RAG/02_langchain.ipynb) | RAG using Redis and LangChain |
| [/RAG/03_llamaindex.ipynb](python-recipes/RAG/03_llamaindex.ipynb) | RAG using Redis and LlamaIndex |
| [/RAG/04_advanced_redisvl.ipynb](python-recipes/RAG/04_advanced_redisvl.ipynb) | Advanced RAG techniques |
| [/RAG/05_nvidia_ai_rag_redis.ipynb](python-recipes/RAG/05_nvidia_ai_rag_redis.ipynb) | RAG using Redis and Nvidia NIMs |
| [/RAG/06_ragas_evaluation.ipynb](python-recipes/RAG/06_ragas_evaluation.ipynb) | Utilize the RAGAS framework to evaluate RAG performance |
| [/RAG/07_user_role_based_rag.ipynb](python-recipes/RAG/07_user_role_based_rag.ipynb) | Implement a simple RBAC policy with vector search using Redis |

### LLM Memory
LLMs are stateless. To maintain context within a conversation chat sessions must be stored and resent to the LLM. Redis manages the storage and retrieval of chat sessions to maintain context and conversational relevance.
| Recipe | Description |
| --- | --- |
| [/llm-session-manager/00_session_manager.ipynb](python-recipes/llm-session-manager/00_llm_session_manager.ipynb) | LLM session manager with semantic similarity |
| [/llm-session-manager/01_multiple_sessions.ipynb](python-recipes/llm-session-manager/01_multiple_sessions.ipynb) | Handle multiple simultaneous chats with one instance |

### Semantic Cache
An estimated 31% of LLM queries are potentially redundant ([source](https://arxiv.org/pdf/2403.02694)). Redis enables semantic caching to help cut down on LLM costs quickly.

| Recipe | Description |
| --- | --- |
| [/semantic-cache/doc2cache_llama3_1.ipynb](python-recipes/semantic-cache/doc2cache_llama3_1.ipynb) | Build a semantic cache using the Doc2Cache framework and Llama3.1 |
| [/semantic-cache/semantic_caching_gemini.ipynb](python-recipes/semantic-cache/semantic_caching_gemini.ipynb) | Build a semantic cache with Redis and Google Gemini |

### Semantic Routing
Routing is a simple and effective way of preventing misuses with your AI application or for creating branching logic between data sources etc.

| Recipe | Description |
| --- | --- |
| [/semantic-router/00_semantic_routing.ipynb](python-recipes/semantic-router/00_semantic_routing.ipynb) | Simple examples of how to build an allow/block list router in addition to a multi-topic router |

### Agents

| Recipe | Description |
| --- | --- |
[/agents/00_langgraph_redis_agentic_rag.ipynb](python-recipes/agents/00_langgraph_redis_agentic_rag.ipynb) | Notebook to get started with lang-graph and agents |
[/agents/01_crewai_langgraph_redis.ipynb](python-recipes/agents/01_crewai_langgraph_redis.ipynb) | Notebook to get started with lang-graph and agents |
[/agents/02_full_featured_agent.ipynb](python-recipes/agents/02_full_featured_agent.ipynb) | Notebook builds full tool calling agent with semantic cache and router |

### Computer Vision
| Recipe | Description |
| ------ | ----------- |
| [/computer-vision/00_facial_recognition_facenet.ipynb](python-recipes/computer-vision/00_facial_recognition_facenet.ipynb) | Build a facial recognition system using the Facenet embedding model and RedisVL.


### Recommendation Systems

| Recipe | Description |
| --- | --- |
| [/recommendation-systems/00_content_filtering.ipynb](python-recipes/recommendation-systems/00_content_filtering.ipynb) | Intro content filtering example with redisvl |
| [/recommendation-systems/01_collaborative_filtering.ipynb](python-recipes/recommendation-systems/01_collaborative_filtering.ipynb) | Intro collaborative filtering example with redisvl |


## Tutorials
Need a *deeper-dive* through different use cases and topics?

| Tutorial | Description | 
| -------- | ------------ |
| [Agentic RAG](https://github.com/redis-developer/agentic-rag) | A tutorial focused on agentic RAG with LlamaIndex and Cohere |
| [RAG on VertexAI](https://github.com/redis-developer/gcp-redis-llm-stack/tree/main) | A RAG tutorial featuring Redis with Vertex AI |
| [Recommendation Systems w/ NVIDIA Merlin & Redis]((https://github.com/redis-developer/redis-nvidia-recsys)) | Three examples, each escalating in complexity, showcasing the process of building a realtime recsys with NVIDIA and Redis |


## Integrations
Redis integrates with many different players in the AI ecosystem. Here's a curated list below:

| Integration | Description |
| --- | --- |
| [RedisVL](https://github.com/redis/redis-vl-python) | A dedicated Python client lib for Redis as a Vector DB |
| [AWS Bedrock](https://redis.io/docs/latest/integrate/amazon-bedrock/) | Streamlines GenAI deployment by offering foundational models as a unified API |
| [LangChain Python](https://github.com/langchain-ai/langchain) | Popular Python client lib for building LLM applications powered by Redis |
| [LangChain JS](https://github.com/langchain-ai/langchainjs) | Popular JS client lib for building LLM applications powered by Redis |
| [LlamaIndex](https://gpt-index.readthedocs.io/en/latest/examples/vector_stores/RedisIndexDemo.html) | LlamaIndex Integration for Redis as a vector Database (formerly GPT-index) |
| [LiteLLM](https://www.litellm.ai/) | Popular LLM proxy layer to help manage and streamline usage of multiple foundation models |
| [Semantic Kernel](https://github.com/microsoft/semantic-kernel/tree/main) | Popular lib by MSFT to integrate LLMs with plugins |
| [RelevanceAI](https://relevance.ai/) | Platform to tag, search and analyze unstructured data faster, built on Redis |
| [DocArray](https://docs.docarray.org/user_guide/storing/index_redis/) | DocArray Integration of Redis as a VectorDB by Jina AI |


# Other Helpful Resources

- [Vector Databases and Large Language Models](https://youtu.be/GJDN8u3Y-T4) - Talk given at LLMs in Production Part 1 by Sam Partee.
- [Level-up RAG with RedisVL](https://redis.io/blog/level-up-rag-apps-with-redis-vector-library/)
- [Improving RAG quality with RAGAs](https://redis.io/blog/get-better-rag-responses-with-ragas/)
- [Vector Databases and AI-powered Search Talk](https://www.youtube.com/watch?v=g2bNHLeKlAg) - Video "Vector Databases and AI-powered Search" given by Sam Partee at SDSC 2023.
- [NVIDIA RecSys with Redis](https://developer.nvidia.com/blog/offline-to-online-feature-storage-for-real-time-recommendation-systems-with-nvidia-merlin/)
- [Benchmarking results for vector databases](https://redis.io/blog/benchmarking-results-for-vector-databases/) - Benchmarking results for vector databases, including Redis and 7 other Vector Database players.
- [Redis Vector Library Docs](https://docs.redisvl.com)
- [Redis Vector Search API Docs](https://redis.io/docs/interact/search-and-query/advanced-concepts/vectors/) - Official Redis literature for Vector Similarity Search.