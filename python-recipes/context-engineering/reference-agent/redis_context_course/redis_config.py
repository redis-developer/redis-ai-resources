"""
Redis configuration and connection management for the Class Agent.

This module handles all Redis connections, including vector storage
and checkpointing.
"""

import os
from typing import Optional
import redis
from redisvl.index import SearchIndex
from redisvl.schema import IndexSchema
from langchain_openai import OpenAIEmbeddings
from langgraph.checkpoint.redis import RedisSaver


class RedisConfig:
    """Redis configuration management."""
    
    def __init__(
        self,
        redis_url: Optional[str] = None,
        vector_index_name: str = "course_catalog",
        checkpoint_namespace: str = "class_agent"
    ):
        self.redis_url = redis_url or os.getenv("REDIS_URL", "redis://localhost:6379")
        self.vector_index_name = vector_index_name
        self.checkpoint_namespace = checkpoint_namespace
        
        # Initialize connections
        self._redis_client = None
        self._vector_index = None
        self._checkpointer = None
        self._embeddings = None
    
    @property
    def redis_client(self) -> redis.Redis:
        """Get Redis client instance."""
        if self._redis_client is None:
            self._redis_client = redis.from_url(self.redis_url, decode_responses=True)
        return self._redis_client
    
    @property
    def embeddings(self) -> OpenAIEmbeddings:
        """Get OpenAI embeddings instance."""
        if self._embeddings is None:
            self._embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        return self._embeddings
    
    @property
    def vector_index(self) -> SearchIndex:
        """Get or create vector search index for courses."""
        if self._vector_index is None:
            schema = IndexSchema.from_dict({
                "index": {
                    "name": self.vector_index_name,
                    "prefix": f"{self.vector_index_name}:",
                    "storage_type": "hash"
                },
                "fields": [
                    {
                        "name": "id",
                        "type": "tag"
                    },
                    {
                        "name": "course_code",
                        "type": "tag"
                    },
                    {
                        "name": "title",
                        "type": "text"
                    },
                    {
                        "name": "description",
                        "type": "text"
                    },
                    {
                        "name": "department",
                        "type": "tag"
                    },
                    {
                        "name": "major",
                        "type": "tag"
                    },
                    {
                        "name": "difficulty_level",
                        "type": "tag"
                    },
                    {
                        "name": "format",
                        "type": "tag"
                    },
                    {
                        "name": "semester",
                        "type": "tag"
                    },
                    {
                        "name": "year",
                        "type": "numeric"
                    },
                    {
                        "name": "credits",
                        "type": "numeric"
                    },
                    {
                        "name": "tags",
                        "type": "tag"
                    },
                    {
                        "name": "content_vector",
                        "type": "vector",
                        "attrs": {
                            "dims": 1536,
                            "distance_metric": "cosine",
                            "algorithm": "hnsw",
                            "datatype": "float32"
                        }
                    }
                ]
            })
            
            self._vector_index = SearchIndex(schema)
            self._vector_index.connect(redis_url=self.redis_url)
            
            # Create index if it doesn't exist
            try:
                self._vector_index.create(overwrite=False)
            except Exception:
                # Index likely already exists
                pass
                
        return self._vector_index
    
    @property
    def checkpointer(self) -> RedisSaver:
        """Get Redis checkpointer for LangGraph state management."""
        if self._checkpointer is None:
            self._checkpointer = RedisSaver(
                redis_client=self.redis_client,
                namespace=self.checkpoint_namespace
            )
            self._checkpointer.setup()
        return self._checkpointer
    
    def health_check(self) -> bool:
        """Check if Redis connection is healthy."""
        try:
            return self.redis_client.ping()
        except Exception:
            return False
    
    def cleanup(self):
        """Clean up connections."""
        if self._redis_client:
            self._redis_client.close()
        if self._vector_index:
            self._vector_index.disconnect()


# Global configuration instance
redis_config = RedisConfig()
