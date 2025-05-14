<div align="center">
<img src="assets/redis-logo.svg" alt="AI Resources" width="175px">

<h1>AI Resources</h1>

<p>
  <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT"></a>
  <a href="#"><img src="https://img.shields.io/github/languages/top/redis-developer/redis-ai-resources" alt="Language"></a>
  <a href="#"><img src="https://img.shields.io/github/last-commit/redis-developer/redis-ai-resources" alt="GitHub last commit"></a>
  <a href="https://discord.gg/redis"><img src="https://img.shields.io/badge/Discord-Redis%20Community-blueviolet" alt="Discord"></a>
  <a href="https://twitter.com/redisinc"><img src="https://img.shields.io/badge/Twitter-@redisinc-blue" alt="Twitter"></a>
</p>

<p>
    ✨ A curated repository of code recipes, demos, tutorials and resources for basic and advanced Redis use cases in the AI ecosystem. ✨
</p>

<div align="center">
  <h3>
    <a href="#getting-started">Getting Started</a> |
    <a href="#demos">Demos</a> |
    <a href="#recipes">Recipes</a> |
    <a href="#tutorials">Tutorials</a> |
    <a href="#integrations">Integrations</a> |
    <a href="#other-helpful-resources">Resources</a>
  </h3>
</div>

</div>
<br>

## Getting Started

New to Redis for AI applications? Here's how to get started:

1. **First time with Redis?** Start with our [Redis Intro notebook](python-recipes/redis-intro/00_redis_intro.ipynb) 
2. **Want to try vector search?** Check our [Vector Search with RedisVL](python-recipes/vector-search/01_redisvl.ipynb) recipe
3. **Building a RAG application?** Begin with [RAG from Scratch](python-recipes/RAG/01_redisvl.ipynb)
4. **Ready to see it in action?** Play with the [Redis RAG Workbench](https://github.com/redis-developer/redis-rag-workbench) demo

<hr>

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

Need quickstarts to begin your Redis AI journey?

### Getting started with Redis & Vector Search

| Recipe | GitHub | Google Colab |
| --- | --- | --- |
| 🏁 **Redis Intro** - The place to start if brand new to Redis | [![Open In GitHub](https://img.shields.io/badge/View-GitHub-green)](python-recipes/redis-intro/00_redis_intro.ipynb) | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/redis-developer/redis-ai-resources/blob/main/python-recipes/redis-intro/00_redis_intro.ipynb) |
| 🔍 **Vector Search with RedisPy** - Vector search with Redis python client | [![Open In GitHub](https://img.shields.io/badge/View-GitHub-green)](python-recipes/vector-search/00_redispy.ipynb) | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/redis-developer/redis-ai-resources/blob/main/python-recipes/vector-search/00_redispy.ipynb) |
| 📚 **Vector Search with RedisVL** - Vector search with Redis Vector Library | [![Open In GitHub](https://img.shields.io/badge/View-GitHub-green)](python-recipes/vector-search/01_redisvl.ipynb) | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/redis-developer/redis-ai-resources/blob/main/python-recipes/vector-search/01_redisvl.ipynb) |
| 🔄 **Hybrid Search** - Hybrid search techniques with Redis (BM25 + Vector) | [![Open In GitHub](https://img.shields.io/badge/View-GitHub-green)](python-recipes/vector-search/02_hybrid_search.ipynb) | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/redis-developer/redis-ai-resources/blob/main/python-recipes/vector-search/02_hybrid_search.ipynb) |
| 🔢 **Data Type Support** - Shows how to convert a float32 index to float16 or integer dataypes | [![Open In GitHub](https://img.shields.io/badge/View-GitHub-green)](python-recipes/vector-search/03_dtype_support.ipynb) | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/redis-developer/redis-ai-resources/blob/main/python-recipes/vector-search/03_dtype_support.ipynb) |


### Retrieval Augmented Generation (RAG)

**Retrieval Augmented Generation** (aka RAG) is a technique to enhance the ability of an LLM to respond to user queries. The **retrieval** part of RAG is supported by a vector database, which can return semantically relevant results to a user's query, serving as contextual information to **augment** the **generative** capabilities of an LLM.

To get started with RAG, either from scratch or using a popular framework like Llamaindex or LangChain, go with these recipes:

| Recipe | GitHub | Google Colab |
| --- | --- | --- |
| 🧩 **RAG from Scratch** - RAG from scratch with the Redis Vector Library | [![Open In GitHub](https://img.shields.io/badge/View-GitHub-green)](python-recipes/RAG/01_redisvl.ipynb) | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/redis-developer/redis-ai-resources/blob/main/python-recipes/RAG/01_redisvl.ipynb) |
| ⛓️ **LangChain RAG** - RAG using Redis and LangChain | [![Open In GitHub](https://img.shields.io/badge/View-GitHub-green)](python-recipes/RAG/02_langchain.ipynb) | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/redis-developer/redis-ai-resources/blob/main/python-recipes/RAG/02_langchain.ipynb) |
| 🦙 **LlamaIndex RAG** - RAG using Redis and LlamaIndex | [![Open In GitHub](https://img.shields.io/badge/View-GitHub-green)](python-recipes/RAG/03_llamaindex.ipynb) | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/redis-developer/redis-ai-resources/blob/main/python-recipes/RAG/03_llamaindex.ipynb) |
| 🚀 **Advanced RAG** - Advanced RAG techniques | [![Open In GitHub](https://img.shields.io/badge/View-GitHub-green)](python-recipes/RAG/04_advanced_redisvl.ipynb) | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/redis-developer/redis-ai-resources/blob/main/python-recipes/RAG/04_advanced_redisvl.ipynb) |
| 🖥️ **NVIDIA RAG** - RAG using Redis and Nvidia NIMs | [![Open In GitHub](https://img.shields.io/badge/View-GitHub-green)](python-recipes/RAG/05_nvidia_ai_rag_redis.ipynb) | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/redis-developer/redis-ai-resources/blob/main/python-recipes/RAG/05_nvidia_ai_rag_redis.ipynb) |
| 📊 **RAGAS Evaluation** - Utilize the RAGAS framework to evaluate RAG performance | [![Open In GitHub](https://img.shields.io/badge/View-GitHub-green)](python-recipes/RAG/06_ragas_evaluation.ipynb) | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/redis-developer/redis-ai-resources/blob/main/python-recipes/RAG/06_ragas_evaluation.ipynb) |
| 🔒 **Role-Based RAG** - Implement a simple RBAC policy with vector search using Redis | [![Open In GitHub](https://img.shields.io/badge/View-GitHub-green)](python-recipes/RAG/07_user_role_based_rag.ipynb) | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/redis-developer/redis-ai-resources/blob/main/python-recipes/RAG/07_user_role_based_rag.ipynb) |

### LLM Memory
LLMs are stateless. To maintain context within a conversation chat sessions must be stored and re-sent to the LLM. Redis manages the storage and retrieval of message histories to maintain context and conversational relevance.

| Recipe | GitHub | Google Colab |
| --- | --- | --- |
| 💬 **Message History** - LLM message history with semantic similarity | [![Open In GitHub](https://img.shields.io/badge/View-GitHub-green)](python-recipes/llm-message-history/00_llm_message_history.ipynb) | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/redis-developer/redis-ai-resources/blob/main/python-recipes/llm-message-history/00_llm_message_history.ipynb) |
| 👥 **Multiple Sessions** - Handle multiple simultaneous chats with one instance | [![Open In GitHub](https://img.shields.io/badge/View-GitHub-green)](python-recipes/llm-message-history/01_multiple_sessions.ipynb) | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/redis-developer/redis-ai-resources/blob/main/python-recipes/llm-message-history/01_multiple_sessions.ipynb) |

### Semantic Caching
An estimated 31% of LLM queries are potentially redundant ([source](https://arxiv.org/pdf/2403.02694)). Redis enables semantic caching to help cut down on LLM costs quickly.

| Recipe | GitHub | Google Colab |
| --- | --- | --- |
| 🧠 **Gemini Semantic Cache** - Build a semantic cache with Redis and Google Gemini | [![Open In GitHub](https://img.shields.io/badge/View-GitHub-green)](python-recipes/semantic-cache/00_semantic_caching_gemini.ipynb) | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/redis-developer/redis-ai-resources/blob/main/python-recipes/semantic-cache/00_semantic_caching_gemini.ipynb) |
| 🦙 **Llama3.1 Doc2Cache** - Build a semantic cache using the Doc2Cache framework and Llama3.1 | [![Open In GitHub](https://img.shields.io/badge/View-GitHub-green)](python-recipes/semantic-cache/01_doc2cache_llama3_1.ipynb) | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/redis-developer/redis-ai-resources/blob/main/python-recipes/semantic-cache/01_doc2cache_llama3_1.ipynb) |
| ⚙️ **Cache Optimization** - Use CacheThresholdOptimizer from redisvl to setup best cache config | [![Open In GitHub](https://img.shields.io/badge/View-GitHub-green)](python-recipes/semantic-cache/02_semantic_cache_optimization.ipynb) | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/redis-developer/redis-ai-resources/blob/main/python-recipes/semantic-cache/02_semantic_cache_optimization.ipynb) |

### Semantic Routing
Routing is a simple and effective way of preventing misuse with your AI application or for creating branching logic between data sources etc.

| Recipe | GitHub | Google Colab |
| --- | --- | --- |
| 🔀 **Basic Routing** - Simple examples of how to build an allow/block list router in addition to a multi-topic router | [![Open In GitHub](https://img.shields.io/badge/View-GitHub-green)](python-recipes/semantic-router/00_semantic_routing.ipynb) | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/redis-developer/redis-ai-resources/blob/main/python-recipes/semantic-router/00_semantic_routing.ipynb) |
| ⚙️ **Router Optimization** - Use RouterThresholdOptimizer from redisvl to setup best router config | [![Open In GitHub](https://img.shields.io/badge/View-GitHub-green)](python-recipes/semantic-router/01_routing_optimization.ipynb) | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/redis-developer/redis-ai-resources/blob/main/python-recipes/semantic-router/01_routing_optimization.ipynb) |


### AI Gateways
AI gateways manage LLM traffic through a centralized, managed layer that can implement routing, rate limiting, caching, and more.

| Recipe | GitHub | Google Colab |
| --- | --- | --- |
| 🚪 **LiteLLM Proxy** - Getting started with LiteLLM proxy and Redis | [![Open In GitHub](https://img.shields.io/badge/View-GitHub-green)](python-recipes/gateway/00_litellm_proxy_redis.ipynb) | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/redis-developer/redis-ai-resources/blob/main/python-recipes/gateway/00_litellm_proxy_redis.ipynb) |


### Agents

| Recipe | GitHub | Google Colab |
| --- | --- | --- |
| 🕸️ **LangGraph Agents** - Notebook to get started with lang-graph and agents | [![Open In GitHub](https://img.shields.io/badge/View-GitHub-green)](python-recipes/agents/00_langgraph_redis_agentic_rag.ipynb) | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/redis-developer/redis-ai-resources/blob/main/python-recipes/agents/00_langgraph_redis_agentic_rag.ipynb) |
| 👥 **CrewAI Agents** - Notebook to get started with CrewAI and lang-graph | [![Open In GitHub](https://img.shields.io/badge/View-GitHub-green)](python-recipes/agents/01_crewai_langgraph_redis.ipynb) | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/redis-developer/redis-ai-resources/blob/main/python-recipes/agents/01_crewai_langgraph_redis.ipynb) |
| 🧠 **Memory Agent** - Building an agent with short term and long term memory using Redis | [![Open In GitHub](https://img.shields.io/badge/View-GitHub-green)](python-recipes/agents/03_memory_agent.ipynb) | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/redis-developer/redis-ai-resources/blob/main/python-recipes/agents/03_memory_agent.ipynb) |
| 🛠️ **Full-Featured Agent** - Notebook builds full tool calling agent with semantic cache and router | [![Open In GitHub](https://img.shields.io/badge/View-GitHub-green)](python-recipes/agents/02_full_featured_agent.ipynb) | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/redis-developer/redis-ai-resources/blob/main/python-recipes/agents/02_full_featured_agent.ipynb) |

### Computer Vision
| Recipe | GitHub | Google Colab |
| ------ | ------ | ------------ |
| 👤 **Facial Recognition** - Build a facial recognition system using the Facenet embedding model and RedisVL | [![Open In GitHub](https://img.shields.io/badge/View-GitHub-green)](python-recipes/computer-vision/00_facial_recognition_facenet.ipynb) | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/redis-developer/redis-ai-resources/blob/main/python-recipes/computer-vision/00_facial_recognition_facenet.ipynb) |


### Recommendation Systems

| Recipe | GitHub | Google Colab |
| --- | --- | --- |
| 📋 **Content Filtering** - Intro content filtering example with redisvl | [![Open In GitHub](https://img.shields.io/badge/View-GitHub-green)](python-recipes/recommendation-systems/00_content_filtering.ipynb) | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/redis-developer/redis-ai-resources/blob/main/python-recipes/recommendation-systems/00_content_filtering.ipynb) |
| 👥 **Collaborative Filtering** - Intro collaborative filtering example with redisvl | [![Open In GitHub](https://img.shields.io/badge/View-GitHub-green)](python-recipes/recommendation-systems/01_collaborative_filtering.ipynb) | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/redis-developer/redis-ai-resources/blob/main/python-recipes/recommendation-systems/01_collaborative_filtering.ipynb) |
| 🏗️ **Two Towers** - Intro deep learning two tower example with redisvl | [![Open In GitHub](https://img.shields.io/badge/View-GitHub-green)](python-recipes/recommendation-systems/02_two_towers.ipynb) | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/redis-developer/redis-ai-resources/blob/main/python-recipes/recommendation-systems/02_two_towers.ipynb) |

### Feature Store
| Recipe | GitHub | Google Colab |
| ------ | ------ | ------------ |
| 💳 **Credit Scoring** - Credit scoring system using Feast with Redis as the online store | [![Open In GitHub](https://img.shields.io/badge/View-GitHub-green)](python-recipes/feature-store/00_feast_credit_score.ipynb) | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/redis-developer/redis-ai-resources/blob/main/python-recipes/feature-store/00_feast_credit_score.ipynb) |
| 🔍 **Transaction Search** - Real-time transaction feature search with Redis | [![Open In GitHub](https://img.shields.io/badge/View-GitHub-green)](python-recipes/feature-store/01_card_transaction_search.ipynb) | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/redis-developer/redis-ai-resources/blob/main/python-recipes/feature-store/01_card_transaction_search.ipynb) |

### ☕️ Java AI Recipes

A set of Java recipes can be found under [/java-recipes](/java-recipes/README.md).


## Tutorials
Need a *deeper-dive* through different use cases and topics?

<table>
  <tr>
    <td align="center" width="33%">
      <b><a href="https://github.com/redis-developer/agentic-rag">🤖 Agentic RAG</a></b>
      <br>
      A tutorial focused on agentic RAG with LlamaIndex and Cohere
    </td>
    <td align="center" width="33%">
      <b><a href="https://github.com/redis-developer/gcp-redis-llm-stack/tree/main">☁️ RAG on VertexAI</a></b>
      <br>
      A RAG tutorial featuring Redis with Vertex AI
    </td>
    <td align="center" width="33%">
      <b><a href="https://github.com/redis-developer/redis-nvidia-recsys">🔍 Recommendation Systems</a></b>
      <br>
      Building realtime recsys with NVIDIA Merlin & Redis
    </td>
  </tr>
</table>

<hr>

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

<hr>

# Other Helpful Resources

- [Vector Databases and Large Language Models](https://youtu.be/GJDN8u3Y-T4) - Talk given at LLMs in Production Part 1 by Sam Partee.
- [Level-up RAG with RedisVL](https://redis.io/blog/level-up-rag-apps-with-redis-vector-library/)
- [Improving RAG quality with RAGAs](https://redis.io/blog/get-better-rag-responses-with-ragas/)
- [Vector Databases and AI-powered Search Talk](https://www.youtube.com/watch?v=g2bNHLeKlAg) - Video "Vector Databases and AI-powered Search" given by Sam Partee at SDSC 2023.
- [NVIDIA RecSys with Redis](https://developer.nvidia.com/blog/offline-to-online-feature-storage-for-real-time-recommendation-systems-with-nvidia-merlin/)
- [Benchmarking results for vector databases](https://redis.io/blog/benchmarking-results-for-vector-databases/) - Benchmarking results for vector databases, including Redis and 7 other Vector Database players.
- [Redis Vector Library Docs](https://docs.redisvl.com)
- [Redis Vector Search API Docs](https://redis.io/docs/interact/search-and-query/advanced-concepts/vectors/) - Official Redis literature for Vector Similarity Search.

<hr>

## Contributing

We welcome contributions to Redis AI Resources! Here's how you can help:

1. **Add a new recipe**: Create a Jupyter notebook demonstrating a Redis AI use case
2. **Improve documentation**: Enhance existing notebooks or README with clearer explanations
3. **Fix bugs**: Address issues in code samples or documentation
4. **Suggest improvements**: Open an issue with ideas for new content or enhancements

To contribute:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

Please follow the existing style and format of the repository when adding content.
