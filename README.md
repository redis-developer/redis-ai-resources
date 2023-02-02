# Redis: AI Resources

<img src="assets/redis-logo.svg" style="width: 130px; float: right;">


✨ A curated list of awesome community resources, integrations, and examples for Redis in the AI ecosystem.



____

### Table of Contents

- Redis as a [Vector Database](#vector-database)
- Redis as an [Online Feature Store](#online-feature-store)
- Redis as an [Inference Engine](#inference-engine)

____

## Vector Database
The following list provides resources, integrations, and examples for **Redis as a Vector Database**.

- Resources
  - [Vector Similarity Search: From Basics to Production](https://mlops.community/vector-similarity-search-from-basics-to-production/) - Introductory blog post to VSS and Redis as a VectorDB.
  - [Redis as a Vector Database](https://vishnudeva.medium.com/redis-as-a-vector-database-rediscloud-2a444c478f3d) - Hackathon review blog post covering Redis as a VectorDB.
  - [Rediscover Redis for Vector Similarity](https://redis.com/blog/rediscover-redis-for-vector-similarity-search/) - Introductory blog post.
  - [AI Powered Document Search](https://datasciencedojo.com/blog/ai-powered-document-search/) - Blog post covering AI Powered Document Search Use Cases & Architectures.
  - [Redis Vector Search Engineering Lab Review](https://mlops.community/redis-vector-search-engineering-lab-review/) - Review of the first Redis VSS Hackathon.
  - [Real-Time Product Recommendation via DocArray and Redis](https://jina.ai/news/real-time-product-recommendation-using-redis-and-docarray/) - Content-based recsys design with Redis as a VectorDB.
  - [Benchmark Vector Search Databases with One Million Data](https://jina.ai/news/benchmark-vector-search-databases-with-one-million-data/) - Jina AI VectorDB benchmarks comparing Redis against others.
  - *Redis + NVIDIA Developer Blog (COMING SOON)*
  - [Redis Vector Search Cheat Sheet by Datascience Dojo](https://drive.google.com/file/d/10O52YXE1-x9jUTv2G-iJUHFSbthWAcyy/view?usp=share_link) - Cheat sheet covering VSS basics.
  - [Redis Vector Similarity Docs](https://redis.io/docs/stack/search/reference/vectors/) - Redis official docs for Vector Search.
  - [Redis-py RediSearch Commands](https://redis.readthedocs.io/en/latest/redismodules.html#redisearch-commands) - Redis-py client library docs for RediSearch.
  - [Redis-py General Docs](https://redis.readthedocs.io/en/latest/) - Redis-py client library docs.
- Integrations/Tools
  - [RedisVL](https://github.com/RedisVentures/redisvl) - new, simplified, and purpose-built Redis VSS Python client library and CLI.
  - [DocArray (by Jina AI)](https://docarray.jina.ai/advanced/document-store/redis/) - DocArry Integration of Redis as a VectorDB.
  - [Haystack <> RedisDocumentStore Example](https://github.com/artefactory/redis-player-one/blob/main/askyves/redis_document_store.py) - Haystack Integration (example) of Redis as a VectorDB.
- Examples
  - [OpenAI Embeddings Q&A](https://github.com/ruoccofabrizio/azure-open-ai-embeddings-qna) - OpenAI and Redis as a Question&Answering service all on Azure.
  - [Redis Vector Search Engineering Lab Submissions](https://github.com/RedisVentures/RedisVentures.github.io/issues/1) - Submissions to the first Redis VSS hackathon.
  - [arXiv CoPilot](https://github.com/artefactory/redisventures-hackunamadata) - Chrome extension that finds relevant/similar academic papers while performing research.
  - [AskYeves Question & Answer App](https://github.com/artefactory/redis-player-one) - QA & Search Engine modeled after the infamous Yves Saint Laurent.
  - [Darwinian Paper Explorer App](https://github.com/artefactory/AreYouRedis) - Explore arXiv scholarly papers over time with topic evolution and search.
  - [arXiv Paper Search](https://github.com/liram11/untitled1-vector-search/) - Semantic search over arXiv scholarly papers.
  - [PapersWithCode Browser Extension](https://github.com/ilhamfp/simpa) - Chrome extension for the PapersWithCode site that finds relevant/similar papers.
  - [TopVecSim](https://github.com/team-castle/topvecsim/)
  - [Redis VSS Streamlit Demo](https://github.com/antonum/Redis-VSS-Streamlit) - Streamlit demo of Redis Vector Search.
  - [Simple Redis Vector Similarity Intro](https://github.com/RedisVentures/simple-vecsim-intro) - Dockerized Jupyter Notebook & Streamlit demo fo Redis Vector Search.
  - [Redis RecSys](https://github.com/RedisVentures/Redis-Recsys) - 3 end-to-end Redis & NVIDIA Recommendation System Architectures.
  - [Redis arXiv Search](https://github.com/RedisVentures/redis-arXiv-search) - Semantic search over arXiv scholarly papers - the original doc search demo app (hosted).
  - [Redis Product Search](https://github.com/RedisVentures/redis-product-search) - eCommerce product search (with image and text) - the original eComm demo app (hosted).
  - [Product Recommendations with DocArray / Jina](https://github.com/jina-ai/product-recommendation-redis-docarray) - Content-based product recommendations example with Redis and DocArray.
  - [Financial News Demo](https://github.com/RedisAI/financial-news) - Financial news vector similarity demo with Redis.
  - [Basic Redis VecSim Demo/Intro](https://github.com/RedisAI/vecsim-demo)

____

## Online Feature Store

- Integrations
  - [Feast]() - open-source Feature Store framework.
  - [Feathr]() - open-source Feature Store framework pioneered by LinkedIn.
  - [Tecton]() - fully-managed Feature Store service.
- Examples
  - [Redis RecSys]() - 3 end-to-end Redis & NVIDIA Recommendation System Architectures showcasing Redis as an online feature store.
  - [Redis + Feast + Triton on GCP]()

----

## Inference Engine

COMING SOON

- Resources
- Integrations
- Examples

____

Have other contributions? Open a PR. We'll happily review.