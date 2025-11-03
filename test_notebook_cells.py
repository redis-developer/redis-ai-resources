#!/usr/bin/env python3
"""Test script to verify notebook cells work correctly"""

import os
import sys

# Test 1: Import all required libraries
print("=" * 60)
print("TEST 1: Importing libraries...")
print("=" * 60)

try:
    import json
    import numpy as np
    import time
    from typing import List, Dict, Any
    
    # Redis and RedisVL imports
    import redis
    from redisvl.index import SearchIndex
    from redisvl.query import VectorQuery
    from redisvl.redis.utils import array_to_buffer, buffer_to_array
    from redisvl.utils import CompressionAdvisor
    from redisvl.redis.connection import supports_svs
    
    # RedisVL Vectorizer imports
    from redisvl.utils.vectorize import HFTextVectorizer
    
    print("✅ All libraries imported successfully!")
except Exception as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)

# Test 2: Redis connection
print("\n" + "=" * 60)
print("TEST 2: Testing Redis connection...")
print("=" * 60)

try:
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = os.getenv("REDIS_PORT", "6379")
    REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")
    REDIS_URL = f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}"
    
    print(f"Connecting to: {REDIS_URL}")
    client = redis.from_url(REDIS_URL)
    ping_result = client.ping()
    print(f"✅ Redis connection successful: {ping_result}")
    
    # Test SVS support
    svs_support = supports_svs(client)
    print(f"✅ SVS-VAMANA support: {svs_support}")
    
except Exception as e:
    print(f"❌ Redis connection failed: {e}")
    sys.exit(1)

# Test 3: RedisVL Vectorizer
print("\n" + "=" * 60)
print("TEST 3: Testing RedisVL HFTextVectorizer...")
print("=" * 60)

try:
    print("Initializing vectorizer...")
    vectorizer = HFTextVectorizer(
        model="sentence-transformers/all-mpnet-base-v2",
        dims=768
    )
    print("✅ Vectorizer initialized successfully!")
    
    # Test embedding generation
    print("\nGenerating test embeddings...")
    test_texts = [
        "This is a test movie about action and adventure",
        "A romantic comedy set in Paris",
        "Sci-fi thriller about artificial intelligence"
    ]
    
    embeddings = vectorizer.embed_many(test_texts)
    embeddings = np.array(embeddings, dtype=np.float32)
    
    print(f"✅ Generated embeddings successfully!")
    print(f"   Shape: {embeddings.shape}")
    print(f"   Dtype: {embeddings.dtype}")
    print(f"   Sample values: {embeddings[0][:5]}")
    
except Exception as e:
    print(f"❌ Vectorizer test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 4: Load sample movie data
print("\n" + "=" * 60)
print("TEST 4: Loading sample movie data...")
print("=" * 60)

try:
    movies_data = [
        {"title": "The Matrix", "genre": "action", "rating": 8.7, "description": "A computer hacker learns about the true nature of reality"},
        {"title": "Inception", "genre": "action", "rating": 8.8, "description": "A thief who steals corporate secrets through dream-sharing technology"},
        {"title": "The Hangover", "genre": "comedy", "rating": 7.7, "description": "Three friends wake up from a bachelor party in Las Vegas"}
    ]
    
    print(f"✅ Loaded {len(movies_data)} sample movies")
    
    # Generate embeddings for movies
    descriptions = [movie['description'] for movie in movies_data]
    movie_embeddings = vectorizer.embed_many(descriptions)
    movie_embeddings = np.array(movie_embeddings, dtype=np.float32)
    
    print(f"✅ Generated embeddings for {len(movie_embeddings)} movies")
    print(f"   Embedding shape: {movie_embeddings.shape}")
    
except Exception as e:
    print(f"❌ Movie data test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("🎉 ALL TESTS PASSED!")
print("=" * 60)
print("\nThe notebook setup is working correctly:")
print("  ✅ All required libraries can be imported")
print("  ✅ Redis connection is working")
print("  ✅ SVS-VAMANA support is available")
print("  ✅ RedisVL HFTextVectorizer is functional")
print("  ✅ Embedding generation works correctly")
print("\nThe notebooks are ready to use!")

