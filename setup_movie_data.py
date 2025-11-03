#!/usr/bin/env python3
"""
Script to populate Redis with movie vector data for Redis Insight visualization
"""

import os
import pandas as pd
import warnings
from redis import Redis

warnings.filterwarnings('ignore')

# Redis connection settings
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = os.getenv("REDIS_PORT", "6379")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")
REDIS_URL = f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}"

print(f"Connecting to Redis at {REDIS_URL}")

# Create Redis client
client = Redis.from_url(REDIS_URL)

# Test connection
try:
    result = client.ping()
    print(f"✅ Redis connection successful: {result}")
except Exception as e:
    print(f"❌ Redis connection failed: {e}")
    exit(1)

# Load movie data
print("📚 Loading movie data...")
try:
    df = pd.read_json("python-recipes/vector-search/resources/movies.json")
    print(f"✅ Loaded {len(df)} movie entries")
    print(df.head())
except Exception as e:
    print(f"❌ Failed to load movie data: {e}")
    exit(1)

# Set up vectorizer
print("🔧 Setting up vectorizer...")
try:
    from redisvl.utils.vectorize import HFTextVectorizer
    from redisvl.extensions.cache.embeddings import EmbeddingsCache
    
    os.environ["TOKENIZERS_PARALLELISM"] = "false"
    
    hf = HFTextVectorizer(
        model="sentence-transformers/all-MiniLM-L6-v2",
        cache=EmbeddingsCache(
            name="embedcache",
            ttl=600,
            redis_client=client,
        )
    )
    print("✅ Vectorizer setup complete")
except Exception as e:
    print(f"❌ Failed to setup vectorizer: {e}")
    exit(1)

# Generate vectors
print("🧮 Generating vectors...")
try:
    df["vector"] = hf.embed_many(df["description"].tolist(), as_buffer=True)
    print("✅ Vectors generated successfully")
except Exception as e:
    print(f"❌ Failed to generate vectors: {e}")
    exit(1)

# Create search index
print("🔍 Creating search index...")
try:
    from redisvl.schema import IndexSchema
    from redisvl.index import SearchIndex
    
    index_name = "movies"
    
    schema = IndexSchema.from_dict({
        "index": {
            "name": index_name,
            "prefix": index_name,
            "storage_type": "hash"
        },
        "fields": [
            {
                "name": "title",
                "type": "text",
            },
            {
                "name": "description",
                "type": "text",
            },
            {
                "name": "genre",
                "type": "tag",
                "attrs": {
                    "sortable": True
                }
            },
            {
                "name": "rating",
                "type": "numeric",
                "attrs": {
                    "sortable": True
                }
            },
            {
                "name": "vector",
                "type": "vector",
                "attrs": {
                    "dims": 384,
                    "distance_metric": "cosine",
                    "algorithm": "flat",
                    "datatype": "float32"
                }
            }
        ]
    })
    
    index = SearchIndex(schema, client)
    index.create(overwrite=True, drop=True)
    print("✅ Search index created successfully")
except Exception as e:
    print(f"❌ Failed to create search index: {e}")
    exit(1)

# Load data into index
print("📥 Loading data into Redis...")
try:
    keys = index.load(df.to_dict(orient="records"))
    print(f"✅ Loaded {len(keys)} movie records into Redis")
    print("Sample keys:", keys[:3])
except Exception as e:
    print(f"❌ Failed to load data: {e}")
    exit(1)

# Verify data
print("🔍 Verifying data...")
try:
    # Check total keys
    all_keys = client.keys("*")
    movie_keys = client.keys("movies:*")
    print(f"✅ Total keys in Redis: {len(all_keys)}")
    print(f"✅ Movie keys: {len(movie_keys)}")
    
    # Check search index
    indexes = client.execute_command('FT._LIST')
    print(f"✅ Search indexes: {indexes}")
    
    # Test a simple search
    from redisvl.query import VectorQuery
    
    query = "action movie with explosions"
    results = index.query(
        VectorQuery(
            vector=hf.embed(query),
            vector_field_name="vector",
            return_fields=["title", "genre", "rating", "description"],
            num_results=3
        )
    )
    
    print(f"✅ Test search for '{query}' returned {len(results)} results:")
    for i, result in enumerate(results, 1):
        print(f"  {i}. {result['title']} ({result['genre']}) - Rating: {result['rating']}")
    
except Exception as e:
    print(f"❌ Verification failed: {e}")

print("\n🎉 Setup complete! Your Redis database now contains:")
print("   - 20 movie records with vector embeddings")
print("   - A searchable 'movies' index")
print("   - Vector search capabilities")
print("\n📊 You can now connect Redis Insight to localhost:6379 to explore the data!")
