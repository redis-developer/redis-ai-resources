# Document Question Answering with Langchain, VertexAI and Redis

![Redis](https://redis.com/wp-content/themes/wpx/assets/images/logo-redis.svg?auto=webp&quality=85,75&width=120)

This a notebook would use LLM (Large Language Model Redis) with Redis Vector Similarity Search and LangChain to answer questions about the information contained in a document.

There are three versions of the notebook, using different LLMs.

- OpenAI - requires OpenAI API key
- Dolly-v2 - no additional requirements, but since the model is running within the notebook runtime, slowest and of the least quality
- Google Gemini - requires active GCP account and Google API key.
- AWS Bedrock - requires AWS access key ID and secret access key

OpenAI notebook requires OpenAI API key. You can find your API key at https://platform.openai.com/account/api-keys.