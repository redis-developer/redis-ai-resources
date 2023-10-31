<img align="right" src="assets/redis-logo.svg" style="width: 130px">

# Redis: AI Resources

✨ A curated list of awesome community resources including content, integrations, documentation and examples for Redis in the AI ecosystem.

## Table of Contents
- Redis as a [Vector Database](#vector-database)
- Redis as a [Feature Store](#feature-store)

----------

## Vector Database
The following list provides resources, integrations, and examples for **Redis as a Vector Database**.

### Integrations/Tools
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

### Examples

#### Quickstarts

| Resource | Description |
| --- | --- |
| [⭐ Hands-On Redis Workshops](https://github.com/Redislabs-Solution-Architects/Redis-Workshops) | Hands-on workshops for Redis JSON, Search, and VSS / Gen AI. |
| [⭐ Redis VSS Getting Started - 3 Ways](https://github.com/Redislabs-Solution-Architects/financial-vss) | Getting started VSS demo covering RedisVL, Redis Python, and LangChain |
| [⭐ OpenAI Cookbook Examples](https://github.com/openai/openai-cookbook/tree/main/examples/vector_databases) | OpenAI Cookbook examples using Redis as a vector database |
| [Redis VSS - Simple Streamlit Demo](https://github.com/antonum/Redis-VSS-Streamlit) | Streamlit demo of Redis Vector Search |
| [Redis VSS - LabLab AI Quickstart](https://github.com/lablab-ai/Vector-Similarity-Search-with-Redis-Quickstart-Notebook) | Quickstart notebook sponspored by LabLab AI for their AI hackathons. |
| [Redis VSS Documentation Quickstart](https://github.com/RedisVentures/redis-vss-getting-started) | Redis.io VSS Quickstart code. |

#### Question & Answer

| Resource | Description | Stars |
| --- | --- | --- |
| [⭐ ArxivChatGuru](https://github.com/RedisVentures/ArxivChatGuru) | Streamlit demo of QnA over Arxiv documents with Redis & OpenAI | ![redis-openai-qna-streamlit-demo-stars] |
| [⭐ Azure OpenAI Embeddings Q&A](https://github.com/ruoccofabrizio/azure-open-ai-embeddings-qna) | OpenAI and Redis as a Q&A service on Azure | ![azure-openai-embeddings-qna-stars] |
| [LLM Document Chat](https://github.com/RedisVentures/LLM-Document-Chat) | Using LlamaIndex and Redis to chat with Documents | ![llm-document-chat-stars] |
| [GCP Vertex AI "Chat Your PDF"](https://github.com/RedisVentures/gcp-redis-llm-stack/tree/main/examples/chat-your-pdf) | Chat with a PDF using Redis & VertexAI LLMs | |
| [LLMChat](https://github.com/c0sogi/LLMChat) | Full-stack implementation using FastAPI, Redis, OpenAI and Flutter. | ![llmchat-stars] |
| [Example eCommerce Chatbot](https://github.com/RedisVentures/redis-langchain-chatbot) | eCommerce Chatbot with Redis, LangChain, and OpenAI | ![redis-langchain-chatbot-stars] |
| [Food-GPT](https://github.com/DevSamurai/food-gpt) | Food-GPT is a QnA Chat System | ![food-gpt-stars] |
| [Redis vector bot](https://github.com/aetherwu/redis-vector-bot) | Redis vector bot for Ecommerce QnA | ![redis-vector-bot-stars] |
| [Local Model QnA Example](https://github.com/cxfcxf/embeddings) | Local LLMs embeddings with Redis as vector db | ![local-model-qna-example-stars] |

#### NLP & Information Retrieval

| Resource | Description | Stars |
| --- | --- | --- |
| [⭐ ChatGPT Retrieval Plugin](https://github.com/openai/chatgpt-retrieval-plugin) | ChatGPT plugin for retrieving personal documents | ![chatgpt-retrieval-plugin-stars] |
| [⭐ Auto-GPT](https://github.com/Torantulino/Auto-GPT) | Experimental OSS app showcasing GPT-4 with Redis as a vectorized memory store | ![auto-gpt-stars]
| [⭐ arXiv Paper Search](https://github.com/RedisVentures/redis-arXiv-search) | Semantic search over arXiv scholarly papers | ![redis-arxiv-search-stars] |
| [⭐ Motörhead](https://github.com/getmetal/motorhead) | Rust-based IR server for LLMs backed by Redis | ![motorhead-stars] |
| [Financial News Demo](https://github.com/RedisAI/financial-news) | Sentiment analysis and Semantic similarity in Financial News articles | ![financial-news-demo-stars] |
| [Romeo GPT](https://github.com/fmanrique8/romeo-gpt) | AI Document management assistant | ![romeo-gpt-stars] |
| [The Pattern](https://github.com/applied-knowledge-systems/the-pattern) | CORD19 medical NLP pipeline with Redis | ![the-pattern-stars] |
| [GPT Vectors Example](https://github.com/gbaeke/gpt-vectors) | Code associated with the blog post below: "Storing and querying embeddings with Redis" | ![gpt-vectors-stars] |
| [Azure OpenAI Redis Deployment Template](https://github.com/RedisVentures/azure-openai-redis-deployment) | Terraform template automates the end-to-end deployment of Azure OpenAI applications using Redis Enterprise as a vector database | ![azure-openai-redis-deployment-stars] |
| [VSS for Finance](https://github.com/redislabs-training/redisfi-vss) | Searching through SEC filings with Redis VSS | ![redisfi-vss-stars] |

#### Recommendation Systems

| Resource | Description | Stars |
| --- | --- | --- |
| [⭐ Redis Merlin RecSys](https://github.com/RedisVentures/Redis-Recsys) | 3 Redis & NVIDIA Merlin Recommendation System Architectures | ![redis-recsys-stars]  |
| [⭐ Visual Product Search](https://github.com/RedisVentures/redis-product-search) | eCommerce product search (with image and text) | ![redis-product-search-stars]  |
| [Product Recommendations with DocArray / Jina](https://github.com/jina-ai/product-recommendation-redis-docarray) |  Content-based product recommendations with Redis and DocArray | ![jina-product-recommendations-stars]  |
| [Amazon Berkeley Product Dataset Demo](https://github.com/RedisAI/vecsim-demo) |  Redis VSS demo on Amazon Berkeley product dataset | ![redis-vecsim-demo-stars]  |

#### Other

| Resource | Description | Stars |
| --- | --- | --- |
| [VectorVerse](https://github.com/abhishek-ch/VectorVerse) | Vector Database comparison app | ![vectorverse-stars] |
| [Simple Vector Similarity Intro](https://github.com/RedisVentures/simple-vecsim-intro) | Dockerized Jupyter Notebook & Streamlit demo of Redis Vector Search | ![redis-vecsim-intro-stars] |
| [Redis Solution Architects VSS Examples](https://github.com/Redislabs-Solution-Architects/vss-ops) | Examples of VSS in Python | ![vss-ops-stars] |
| [TopVecSim](https://github.com/team-castle/topvecsim/) | Topic Similarity with Redis VSS | ![top-vecsim-stars] |
| [Java Demo](https://github.com/RedisAI/Java-VSS-demo) | Redis VSS demo in Java | ![java-demo-stars] |
| [Redis VSS Go template](https://github.com/dathan/go-vector-embedding) | Redis VSS template in Go | ![redis-vss-go-template-stars] |
| [Redis VSS Demo](https://github.com/bsbodden/roms-vss-celebs) | Redis VSS demo with celebrity faces | ![celeb-faces-stars] |

#### [Redis Vector Search Engineering Lab Submissions](https://github.com/RedisVentures/RedisVentures.github.io/issues/1) - Submissions to the first Redis VSS hackathon.

| Resource | Description | Stars |
| --- | --- | --- |
| [arXiv CoPilot](https://github.com/artefactory/redisventures-hackunamadata) | Chrome extension that finds relevant/similar academic papers while performing research | ![arxiv-copilot-stars] |
| [AskYeves Question & Answer App](https://github.com/artefactory/redis-player-one) | QA & Search Engine modeled after the infamous Yves Saint Laurent | ![askyeves-stars] |
| [Darwinian Paper Explorer App](https://github.com/artefactory/AreYouRedis) | Explore arXiv scholarly papers over time with topic evolution and search | ![darwinian-paper-explorer-stars] |
| [PapersWithCode Browser Extension](https://github.com/ilhamfp/simpa) | Chrome extension for the PapersWithCode site that finds relevant/similar papers | ![paperswithcode-stars] |
| [Document Search + CLI](https://github.com/artefactory/redis-team-THM) | Search engine for documents with a CLI | ![document-search-cli-stars] |


###  RediSearch Clients
| Client | Language | License | Stars |
| --- | --- | --- | --- |
| [Redis-Py](https://github.com/redis/redis-py) | Python | MIT | ![redis-py-stars] |
| [RedisVL](https://github.com/RedisVentures/redisvl) | Python (*Alpha*) | MIT| ![redisvl-stars] |
| [jedis][jedis-url] | Java | MIT |  ![Stars][jedis-stars] |
| [node-redis][node-redis-url] | Node.js | MIT | ![Stars][node-redis-stars] |
| [nredisstack][nredisstack-url] | .NET | MIT |  ![Stars][nredisstack-stars] |
| [redisearch-go][redisearch-go-url] | Go | BSD | [![redisearch-go-stars]][redisearch-go-url] |
| [redisearch-api-rs][redisearch-api-rs-url] | Rust | BSD | [![redisearch-api-rs-stars]][redisearch-api-rs-url] |

For a full list of RediSearch clients, see [RediSearch Clients](https://redis.io/docs/stack/search/clients/).
For a full list of Redis Clients see [Redis Clients](https://redis.io/resources/clients/).

### Content
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

### Benchmarks
- [Vector Database Benchmarks](https://jina.ai/news/benchmark-vector-search-databases-with-one-million-data/) - Jina AI VectorDB benchmarks comparing Redis against others.
- [ANN Benchmarks](https://ann-benchmarks.com) - Standard ANN Benchmarks site. *Only using single Redis OSS instance/client.*

### Documentation
- [Redis Vector Database QuickStart](https://redis.io/docs/get-started/vector-database/)
- [Redis Vector Similarity Docs](https://redis.io/docs/interact/search-and-query/advanced-concepts/vectors/) - Official Redis literature for Vector Similarity Search.
- [Redis-py Search Docs](https://redis.readthedocs.io/en/latest/redismodules.html#redisearch-commands) - Redis-py client library docs for RediSearch.
- [Redis-py General Docs](https://redis.readthedocs.io/en/latest/) - Redis-py client library documentation.
- [Redis Stack](https://redis.io/docs/stack/) - Redis Stack documentation.
- [Redis Clients](https://redis.io/docs/clients/) - Redis client list.



[openai-cookbook-stars]: https://img.shields.io/github/stars/openai/openai-cookbook?style=social
[redis-openai-qna-streamlit-demo-stars]: https://img.shields.io/github/stars/RedisVentures/redis-openai-qna?style=social
[redis-py-stars]: https://img.shields.io/github/stars/redis/redis-py?style=social
[redisvl-stars]: https://img.shields.io/github/stars/RedisVentures/redisvl?style=social
[redis-py-url]: https://github.com/redis/redis-py
[redis-py-stars]: https://img.shields.io/github/stars/redis/redis-py.svg?style=social&amp;label=Star&amp;maxAge=2592000
[jedis-url]: https://github.com/redis/jedis
[jedis-stars]: https://img.shields.io/github/stars/redis/jedis.svg?style=social&amp;label=Star&amp;maxAge=2592000
[nredisstack-url]: https://github.com/redis/nredisstack
[nredisstack-stars]: https://img.shields.io/github/stars/redis/nredisstack.svg?style=social&amp;label=Star&amp;maxAge=2592000
[node-redis-url]: https://github.com/redis/node-redis
[node-redis-stars]: https://img.shields.io/github/stars/redis/node-redis.svg?style=social&amp;label=Star&amp;maxAge=2592000
[redisearch-go-url]: https://github.com/RediSearch/redisearch-go
[redisearch-go-stars]: https://img.shields.io/github/stars/RediSearch/redisearch-go.svg?style=social&amp;label=Star&amp;maxAge=2592000
[redisearch-api-rs-url]: https://github.com/RediSearch/redisearch-api-rs
[redisearch-api-rs-stars]: https://img.shields.io/github/stars/RediSearch/redisearch-api-rs.svg?style=social&amp;label=Star&amp;maxAge=2592000
[java-demo-stars]: https://img.shields.io/github/stars/RedisAI/Java-VSS-demo.svg?style=social&amp;label=Star&amp;maxAge=2592000
[top-vecsim-stars]: https://img.shields.io/github/stars/team-castle/topvecsim.svg?style=social&amp;label=Star&amp;maxAge=2592000
[document-search-cli-stars]: https://img.shields.io/github/stars/artefactory/redis-team-THM.svg?style=social&amp;label=Star&amp;maxAge=2592000
[paperswithcode-stars]: https://img.shields.io/github/stars/ilhamfp/simpa.svg?style=social&amp;label=Star&amp;maxAge=2592000
[darwinian-paper-explorer-stars]: https://img.shields.io/github/stars/artefactory/AreYouRedis.svg?style=social&amp;label=Star&amp;maxAge=2592000
[askyeves-stars]: https://img.shields.io/github/stars/artefactory/redis-player-one.svg?style=social&amp;label=Star&amp;maxAge=2592000
[arxiv-copilot-stars]: https://img.shields.io/github/stars/artefactory/redisventures-hackunamadata.svg?style=social&amp;label=Star&amp;maxAge=2592000
[the-pattern-stars]: https://img.shields.io/github/stars/applied-knowledge-systems/the-pattern.svg?style=social&amp;label=Star&amp;maxAge=2592000
[financial-news-demo-stars]: https://img.shields.io/github/stars/RedisAI/financial-news.svg?style=social&amp;label=Star&amp;maxAge=2592000
[redis-vecsim-intro-stars]: https://img.shields.io/github/stars/RedisVentures/simple-vecsim-intro.svg?style=social&amp;label=Star&amp;maxAge=2592000
[redis-vss-streamlit-demo-stars]: https://img.shields.io/github/stars/antonum/Redis-VSS-Streamlit.svg?style=social&amp;label=Star&amp;maxAge=2592000
[redis-arxiv-search-stars]: https://img.shields.io/github/stars/RedisVentures/redis-arXiv-search.svg?style=social&amp;label=Star&amp;maxAge=2592000
[azure-openai-embeddings-qna-stars]: https://img.shields.io/github/stars/ruoccofabrizio/azure-open-ai-embeddings-qna.svg?style=social&amp;label=Star&amp;maxAge=2592000
[redis-recsys-stars]: https://img.shields.io/github/stars/redisventures/redis-recsys.svg?style=social&amp;label=Star&amp;maxAge=2592000
[redis-product-search-stars]: https://img.shields.io/github/stars/redisventures/redis-product-search.svg?style=social&amp;label=Star&amp;maxAge=2592000
[jina-product-recommendations-stars]: https://img.shields.io/github/stars/jina-ai/product-recommendation-redis-docarray.svg?style=social&amp;label=Star&amp;maxAge=2592000
[redis-vecsim-demo-stars]: https://img.shields.io/github/stars/redisai/vecsim-demo.svg?style=social&amp;label=Star&amp;maxAge=2592000
[chatgpt-retrieval-plugin-stars]: https://img.shields.io/github/stars/openai/chatgpt-retrieval-plugin?style=social
[motorhead-stars]: https://img.shields.io/github/stars/getmetal/motorhead?style=social
[redis-langchain-chatbot-stars]: https://img.shields.io/github/stars/RedisVentures/redis-langchain-chatbot?style=social
[gpt-vectors-stars]: https://img.shields.io/github/stars/gbaeke/gpt-vectors?style=social
[vss-ops-stars]: https://img.shields.io/github/stars/Redislabs-Solution-Architects/vss-ops?style=social
[lablab-vss-quickstart]: https://img.shields.io/github/stars/lablab-ai/Vector-Similarity-Search-with-Redis-Quickstart-Notebook?style=social
[auto-gpt-stars]: https://img.shields.io/github/stars/Torantulino/Auto-GPT?style=social
[romeo-gpt-stars]: https://img.shields.io/github/stars/fmanrique8/romeo-gpt?style=social
[celeb-faces-stars]: https://img.shields.io/github/stars/bsbodden/roms-vss-celebs?style=social
[redis-vector-bot-stars]: https://img.shields.io/github/stars/aetherwu/redis-vector-bot?style=social
[redis-vss-go-template-stars]: https://img.shields.io/github/stars/dathan/go-vector-embedding?style=social
[redisfi-vss-stars]: https://img.shields.io/github/stars/redislabs-training/redisfi-vss?style=social
[llm-document-chat-stars]: https://img.shields.io/github/stars/RedisVentures/llm-document-chat?style=social
[food-gpt-stars]: https://img.shields.io/github/stars/DevSamurai/food-gpt?style=social
[llmchat-stars]: https://img.shields.io/github/stars/c0sogi/llmchat?style=social
[vectorverse-stars]: https://img.shields.io/github/stars/abhishek-ch/vectorverse?style=social
[local-model-qna-example-stars]: https://img.shields.io/github/stars/cxfcxf/embeddings?style=social
[azure-openai-redis-deployment-stars]: https://img.shields.io/github/stars/RedisVentures/azure-openai-redis-deployment?style=social

____

## Feature Store
The following list provides resources, integrations, and examples for **Redis as a Feature Store**.

### Examples

#### Recommendation Systems

| Resource | Description | Stars |
| --- | --- | --- |
| [⭐ Redis Merlin RecSys](https://github.com/RedisVentures/Redis-Recsys) | Redis & NVIDIA Merlin Recommendation System architectures | ![redis-recsys-stars] |
| [Market-basket-analysis](https://github.com/RedisLabs-Field-Engineering/demo-market-basket-analysis) | An exmaple of predicting shopping baskets on passed purchases | ![market-basket-analysis-stars] |


#### Life Sciences / Healthcare

| Resource | Description | Stars |
| --- | --- | --- |
| [⭐ Redis Vaccine Forecaster](https://github.com/RedisVentures/redis-feast-gcp) | End-to-end ML system to predict vaccine demand deployed in GCP with Redis, Feast, Triton, and Vertex AI. | ![redis-vaccine-forecaster-stars] |

#### Image/Video

| Resource | Description | Stars |
| --- | --- | --- |
| [Animal Recognition Demo](https://github.com/RedisGears/AnimalRecognitionDemo) | An example of using Redis Streams, RedisGears and RedisAI for Realtime Video Analytics (i.e. filtering cats) | ![animal-recog-stars] |
| [Realtime Video Analytics](https://github.com/RedisGears/EdgeRealtimeVideoAnalytics) | An example of using Redis Streams, RedisGears, RedisAI and RedisTimeSeries for Realtime Video Analytics (i.e. counting people) | ![realtime-video-analytics-stars] |


#### Finance

| Resource | Description | Stars |
| --- | --- | --- |
| [Redis + Feast + Ray Demo](https://github.com/RedisVentures/redis-feast-ray) | A demo pipeline using Redis as an online feature store with Feast for orchestration and Ray for training and model serving | ![redis-vaccine-forecaster-stars] |
| [⭐ Loan Prediction Example](https://github.com/RedisVentures/loan-prediction-microservice) | Loan prediction example with Redis as the feature store and serving layer. | ![load-prediction-example-stars] |

#### Other

| Resource | Description | Stars |
| --- | --- | --- |
| [Redis SQL](https://github.com/redis-field-engineering/redis-sql-trino) | Indexed SQL queries on Redis data using Trino | ![redis-sql-stars] |
| [Redis GraphQL](https://github.com/redis-field-engineering/redis-graphql) | GraphQL queries on Redis data | ![redis-graphql-stars] |
| [RedisAI Examples](https://github.com/RedisAI/redisai-examples) | A collection of examples using RedisAI | ![redisai-examples-stars] |


### Materialization and Orchestration

| Resource | Description | Stars |
| --- | --- | --- |
| [⭐ Spark-Redis](https://github.com/RedisLabs/spark-redis) | Spark-Redis is a connector that allows you to stream data from Spark to Redis | ![spark-redis-stars] |
| [⭐ Feast](https://github.com/feast-dev/feast) | Feast feature orchestration system framework | ![feast-stars] |
| [Feathr](https://github.com/linkedin/feathr) | Feathr is a feature orchestration framework created by Linkedin | ![feathr-stars] |
| [Redis Kafka](https://github.com/redis-field-engineering/redis-kafka-connect) | Redis Kafka Connect is a connector that allows you to stream data from Kafka to Redis | ![redis-sql-stars] |


### Content
- [What is a Feature Store?](https://www.tecton.ai/blog/what-is-a-feature-store/) - introductory blog post on feature stores
- [Building a Gigascale Feature Store with Redis](https://doordash.engineering/2020/11/19/building-a-gigascale-ml-feature-store-with-redis/) - blog post on DoorDash's feature store architecture
- [Feature Store Comparison](https://mlops.community/learn/feature-store/) - comparison between a few feature store options.
- [Feature Storage with Feast and Redis](https://redis.com/blog/building-feature-stores-with-redis-introduction-to-feast-with-redis/) - blog post outlining basic Redis+Feast usage.

### Benchmarks
- [Feast Feature Serving Benchmarks](https://feast.dev/blog/feast-benchmarks/) - Feast-published benchmarks on Redis vs DynamoDB vs Datastore for feature retrieval.

### Documentation
- [Redis-py General Docs](https://redis.readthedocs.io/en/latest/) - Redis-py client library documentation.
- [RedisJSON](https://github.com/RedisJSON) - RedisJSON Module.
- [RedisAI](https://github.com/RedisAI/RedisAI) - RedisAI Module.
- [RedisTimeSeries](https://github.com/RedisTimeSeries/RedisTimeSeries) - Redis Time Series Module.
- [RedisConnect](https://github.com/redis-field-engineering/redis-connect-dist) - a distributed platform that enables real-time event streaming, transformation, and propagation of changed-data events from heterogeneous data platforms to Redis.
### Integrations
- [FeatureForm](https://www.featureform.com/?gclid=Cj0KCQjw_r6hBhDdARIsAMIDhV_lhReZdfM66Z5gE5yJCtDsSb3WeLhHjtI4AFokk_cjKC54vRDXN7waAq3HEALw_wcB) - open-source Feature Store orchestration framework.
- [Feast](https://docs.feast.dev/reference/online-stores/redis) - open-source Feature Store orchestration framework.
- [Feathr](https://github.com/feathr-ai/feathr) - open-source Feature Store orchestration framework pioneered by LinkedIn.
- [Tecton](https://www.tecton.ai/blog/announcing-support-for-redis/) - fully-managed Feature Store service.


[redis-graphql-stars]: https://img.shields.io/github/stars/redis-field-engineering/redis-graphql.svg?style=social&amp;label=Star&amp;maxAge=2592000
[spark-redis-stars]: https://img.shields.io/github/stars/RedisLabs/spark-redis.svg?style=social&amp;label=Star&amp;maxAge=2592000

[feathr-stars]: https://img.shields.io/github/stars/linkedin/feathr.svg?style=social&amp;label=Star&amp;maxAge=2592000
[feast-stars]: https://img.shields.io/github/stars/feast-dev/feast.svg?style=social&amp;label=Star&amp;maxAge=2592000

[load-prediction-example-stars]: https://img.shields.io/github/stars/RedisVentures/loan-prediction-microservice.svg?style=social&amp;label=Star&amp;maxAge=2592000
[redis-feast-ray-demo-stars]: https://img.shields.io/github.com/RedisVentures/redis-feast-ray.svg?style=social&amp;label=Star&amp;maxAge=2592000
[redis-vaccine-forecaster-stars]: https://img.shields.io/github/stars/RedisVentures/redis-feast-gcp.svg?style=social&amp;label=Star&amp;maxAge=2592000

[redis-kafka-connect-stars]: https://img.shields.io/github/stars/redis-field-engineering/redis-kafka-connect.svg?style=social&amp;label=Star&amp;maxAge=2592000

[redisai-examples-stars]: https://img.shields.io/github/stars/RedisAI/redisai-examples.svg?style=social&amp;label=Star&amp;maxAge=2592000

[realtime-video-analytics-stars]: https://img.shields.io/github/stars/RedisGears/EdgeRealtimeVideoAnalytics.svg?style=social&amp;label=Star&amp;maxAge=2592000
[animal-recog-stars]: https://img.shields.io/github/stars/RedisGears/AnimalRecognitionDemo.svg?style=social&amp;label=Star&amp;maxAge=2592000

[market-basket-analysis-stars]: https://img.shields.io/github/stars/RedisLabs-Field-Engineering/demo-market-basket-analysis.svg?style=social&amp;label=Star&amp;maxAge=2592000

[redis-sql-stars]: https://img.shields.io/github/stars/redis-field-engineering/redis-sql-trino.svg?style=social&amp;label=Star&amp;maxAge=2592000



----



*Have other contributions? [Checkout our contributing guidelines](contributing.md).*
