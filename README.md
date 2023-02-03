<img align="right" src="assets/redis-logo.svg" style="width: 110px">

# Redis: AI Resources



✨ A curated list of awesome community resources, integrations, and examples for Redis in the AI ecosystem.

### Table of Contents

- Redis as a [Vector Database](#vector-database)
- Redis as a [Feature Store](#feature-store)

____

## Vector Database
The following list provides resources, integrations, and examples for **Redis as a Vector Database**.

- Content
  - [Vector Similarity Search: From Basics to Production](https://mlops.community/vector-similarity-search-from-basics-to-production/) - Introductory blog post to VSS and Redis as a VectorDB.
  - [AI-Powered Document Search](https://datasciencedojo.com/blog/ai-powered-document-search/) - Blog post covering AI Powered Document Search Use Cases & Architectures.
  - [Engineering Lab Review](https://mlops.community/redis-vector-search-engineering-lab-review/) - Review of the first Redis VSS Hackathon.
  - [Vector Database Benchmarks](https://jina.ai/news/benchmark-vector-search-databases-with-one-million-data/) - Jina AI VectorDB benchmarks comparing Redis against others.
  - [Real-Time Product Recommendations](https://jina.ai/news/real-time-product-recommendation-using-redis-and-docarray/) - Content-based recsys design with Redis and DocArray.
  - [Redis as a Vector Database](https://vishnudeva.medium.com/redis-as-a-vector-database-rediscloud-2a444c478f3d) - Hackathon review blog post covering Redis as a VectorDB.
  - [Building Intelligent Apps with Redis Vector Similarity Search](https://redis.com/blog/build-intelligent-apps-redis-vector-similarity-search/) - Introductory blog post.
  - [Rediscovering Redis for Vector Similarity](https://redis.com/blog/rediscover-redis-for-vector-similarity-search/) - Introductory blog post.
  - [VSS Cheat Sheet](https://drive.google.com/file/d/10O52YXE1-x9jUTv2G-iJUHFSbthWAcyy/view?usp=share_link) - Redis Vector Search Cheat Sheet by Datascience Dojo.
  - [RedisDays Keynote](https://www.youtube.com/watch?v=EEIBTEpb2LI) - Video "Infuse Real-Time AI Into Your "Financial Services" Application".
  - [RedisDays Trading Signals](https://www.youtube.com/watch?v=_Lrbesg4DhY) - Video "Using AI to Reveal Trading Signals Buried in Corporate Filings".
  - *Redis + NVIDIA Developer Blog (COMING SOON)*
- Documentation
  - [Redis Vector Similarity Docs](https://redis.io/docs/stack/search/reference/vectors/) - Redis official docs for Vector Search.
  - [Redis-py Search Docs](https://redis.readthedocs.io/en/latest/redismodules.html#redisearch-commands) - Redis-py client library docs for RediSearch.
  - [Redis-py General Docs](https://redis.readthedocs.io/en/latest/) - Redis-py client library documentation.
  - [Red
  Search](https://github.com/RediSearch/RediSearch) - RediSearch Module.
  - [Redis Stack](https://redis.io/docs/stack/) - Redis Stack documentation.
  - [Redis Clients](https://redis.io/docs/clients/) - Redis client list.
- Integrations/Tools
  - [RedisVL](https://github.com/RedisVentures/redisvl) - new, OSS, and purpose-built Redis VSS Python client library and CLI (*alpha*).
  - [DocArray](https://docarray.jina.ai/advanced/document-store/redis/) - DocArray Integration of Redis as a VectorDB by Jina AI.
  - [Haystack Example](https://github.com/artefactory/redis-player-one/blob/main/askyves/redis_document_store.py) - Haystack Integration (example) of Redis as a VectorDB.
  - [RelevanceAI](https://relevance.ai/) - Platform to ag, search and analyze unstructured data faster, built on Redis.
- Examples
  - [⭐ Azure OpenAI Embeddings Q&A](https://github.com/ruoccofabrizio/azure-open-ai-embeddings-qna) - OpenAI and Redis as a Q&A service on Azure.
  - [⭐ Redis Merlin RecSys](https://github.com/RedisVentures/Redis-Recsys) - 3 end-to-end Redis & NVIDIA Merlin Recommendation System Architectures.
  - [Redis Vector Search Engineering Lab Submissions](https://github.com/RedisVentures/RedisVentures.github.io/issues/1) - Submissions to the first Redis VSS hackathon.
    - [⭐ arXiv Paper Search](https://github.com/RedisVentures/redis-arXiv-search) - Semantic search over arXiv scholarly papers - the original doc search demo app (hosted).
    - [⭐ arXiv CoPilot](https://github.com/artefactory/redisventures-hackunamadata) - Chrome extension that finds relevant/similar academic papers while performing research.
    - [AskYeves Question & Answer App](https://github.com/artefactory/redis-player-one) - QA & Search Engine modeled after the infamous Yves Saint Laurent.
    - [Darwinian Paper Explorer App](https://github.com/artefactory/AreYouRedis) - Explore arXiv scholarly papers over time with topic evolution and search.
    - [PapersWithCode Browser Extension](https://github.com/ilhamfp/simpa) - Chrome extension for the PapersWithCode site that finds relevant/similar papers.
    - [Document Search + CLI](https://github.com/artefactory/redis-team-THM)
  - [⭐ Product Search](https://github.com/RedisVentures/redis-product-search) - eCommerce product search (with image and text) - the original eComm demo app (hosted).
  - [Redis VSS Streamlit Demo](https://github.com/antonum/Redis-VSS-Streamlit) - Streamlit demo of Redis Vector Search.
  - [Simple Vector Similarity Intro](https://github.com/RedisVentures/simple-vecsim-intro) - Dockerized Jupyter Notebook & Streamlit demo fo Redis Vector Search.
  - [Product Recommendations with DocArray / Jina](https://github.com/jina-ai/product-recommendation-redis-docarray) - Content-based product recommendations example with Redis and DocArray.
  - [TopVecSim](https://github.com/team-castle/topvecsim/) - Topic Similarity with Redis VSS.
  - [Java Demo](https://github.com/RedisAI/Java-VSS-demo) - Redis VSS demo in Java.
  - [Financial News Demo](https://github.com/RedisAI/financial-news) - Sentiment analysis and Semantic similarity in Financial News articles
  - [Berkeley Dataset Demo](https://github.com/RedisAI/vecsim-demo) - Redis VSS demo on Berkeley dataset.

____

## Feature Store

- Content
  - [What is a Feature Store?](https://www.tecton.ai/blog/what-is-a-feature-store/) - introductory blog post on feature stores.
  - [Feature Store Comparison](https://mlops.community/learn/feature-store/) - comparison between a few feature store options.
  - [Feature Storage with Feast and Redis](https://redis.com/blog/building-feature-stores-with-redis-introduction-to-feast-with-redis/) - blog post outlining basic Redis+Feast usage.
  - [Feast Feature Serving Benchmarks](https://feast.dev/blog/feast-benchmarks/) - Feast-published benchmarks on Redis vs DynamoDB vs Datastore for feature retrieval.
- Documentation
  - [Redis-py General Docs](https://redis.readthedocs.io/en/latest/) - Redis-py client library documentation.
  - [RedisJSON](https://github.com/RedisJSON) - RedisJSON Module.
  - [RedisAI](https://github.com/RedisAI/RedisAI) - RedisAI Module.
  - [RedisTimeSeries](https://github.com/RedisTimeSeries/RedisTimeSeries) - Redis Time Series Module.
  - [RedisConnect](https://github.com/redis-field-engineering/redis-connect-dist) - a distributed platform that enables real-time event streaming, transformation, and propagation of changed-data events from heterogeneous data platforms to Redis.
- Integrations
  - [Feast](https://docs.feast.dev/reference/online-stores/redis) - open-source Feature Store orchestration framework.
  - [Tecton](https://www.tecton.ai/blog/announcing-support-for-redis/) - fully-managed Feature Store service.
  - [Feathr](https://github.com/feathr-ai/feathr) - open-source Feature Store orchestration framework pioneered by LinkedIn.
- Examples
  - [⭐ Redis Merlin RecSys](https://github.com/RedisVentures/Redis-Recsys) - 3 end-to-end Redis & NVIDIA Merlin Recommendation System Architectures showcasing Redis as an online feature store.
  - [⭐ Redis + Feast + Triton on GCP](https://github.com/RedisVentures/redis-feast-gcp) - End-to-end ML system deployed in GCP with Redis, Feast, Triton, and Vertex AI.
  - [Redis + Feast + Ray Demo](https://github.com/RedisVentures/redis-feast-ray) - a demo pipeline using Redis as an online feature store with Feast for orchestration and Ray for training and model serving
  - [Load Prediction Example](https://github.com/RedisVentures/loan-prediction-microservice) - load prediction example with Redis as the feature store and serving layer.

----


*Have other contributions? Open a PR. We'll happily review.*