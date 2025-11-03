#!/usr/bin/env python3
"""
Test script to verify the key cells from migration notebooks work correctly.
This simulates running the notebooks in order.
"""

import os
import sys
import json
import numpy as np
import time
from typing import List, Dict, Any

print("=" * 70)
print("TESTING MIGRATION NOTEBOOK CELLS")
print("=" * 70)

# Test 1: Import all required libraries
print("\n[1/8] Testing imports...")
try:
    import redis
    from redisvl.index import SearchIndex
    from redisvl.query import VectorQuery
    from redisvl.redis.utils import array_to_buffer, buffer_to_array
    from redisvl.utils import CompressionAdvisor
    from redisvl.redis.connection import supports_svs
    from redisvl.utils.vectorize import HFTextVectorizer
    print("✅ All imports successful")
except Exception as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)

# Test 2: Redis connection
print("\n[2/8] Testing Redis connection...")
try:
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = os.getenv("REDIS_PORT", "6379")
    REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")
    REDIS_URL = f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}"
    
    client = redis.from_url(REDIS_URL)
    ping_result = client.ping()
    print(f"✅ Redis connection: {ping_result}")
    
    # Get Redis version
    info = client.info()
    redis_version = info.get('redis_version', 'unknown')
    print(f"   Redis version: {redis_version}")
except Exception as e:
    print(f"❌ Redis connection failed: {e}")
    sys.exit(1)

# Test 3: SVS support
print("\n[3/8] Testing SVS-VAMANA support...")
try:
    svs_supported = supports_svs(client)
    print(f"✅ SVS-VAMANA support: {svs_supported}")
    if not svs_supported:
        print("⚠️  Warning: SVS-VAMANA not supported (requires Redis Stack 8.2.0+)")
except Exception as e:
    print(f"❌ SVS support check failed: {e}")

# Test 4: Load sample data
print("\n[4/8] Loading sample movie data...")
try:
    movies_data = [
        {"title": "The Matrix", "genre": "action", "rating": 8.7, 
         "description": "A computer hacker learns about the true nature of reality"},
        {"title": "Inception", "genre": "action", "rating": 8.8, 
         "description": "A thief who steals corporate secrets through dream-sharing technology"},
        {"title": "The Hangover", "genre": "comedy", "rating": 7.7, 
         "description": "Three friends wake up from a bachelor party in Las Vegas"}
    ]
    print(f"✅ Loaded {len(movies_data)} sample movies")
except Exception as e:
    print(f"❌ Failed to load sample data: {e}")
    sys.exit(1)

# Test 5: CompressionAdvisor (CRITICAL TEST - this was the bug)
print("\n[5/8] Testing CompressionAdvisor...")
try:
    dims = 768
    config = CompressionAdvisor.recommend(dims=dims, priority="memory")
    
    # Test object attribute access (not dictionary access)
    print(f"✅ CompressionAdvisor returned: {type(config)}")
    print(f"   Algorithm: {config.algorithm}")
    print(f"   Datatype: {config.datatype}")
    
    # Test optional attributes with hasattr
    if hasattr(config, 'compression'):
        print(f"   Compression: {config.compression}")
    else:
        print(f"   Compression: None")
    
    if hasattr(config, 'reduce'):
        print(f"   Reduce dims: {dims} → {config.reduce}")
    else:
        print(f"   Reduce dims: No reduction")
    
    print("✅ CompressionAdvisor API working correctly (object attributes)")
except Exception as e:
    print(f"❌ CompressionAdvisor failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 6: HFTextVectorizer initialization
print("\n[6/8] Testing HFTextVectorizer initialization...")
try:
    vectorizer = HFTextVectorizer(
        model="sentence-transformers/all-mpnet-base-v2"  # dims is auto-detected
    )
    print("✅ HFTextVectorizer initialized successfully")
except Exception as e:
    print(f"❌ HFTextVectorizer initialization failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 7: Generate embeddings
print("\n[7/8] Testing embedding generation...")
try:
    descriptions = [movie['description'] for movie in movies_data]
    print(f"   Generating embeddings for {len(descriptions)} descriptions...")
    
    embeddings = vectorizer.embed_many(descriptions)
    embeddings = np.array(embeddings, dtype=np.float32)
    
    print(f"✅ Generated embeddings successfully")
    print(f"   Shape: {embeddings.shape}")
    print(f"   Dtype: {embeddings.dtype}")
    print(f"   Sample values: {embeddings[0][:3]}")
except Exception as e:
    print(f"❌ Embedding generation failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 8: Create SVS index with config object
print("\n[8/8] Testing SVS index creation with CompressionAdvisor config...")
try:
    # Get config
    selected_config = CompressionAdvisor.recommend(dims=dims, priority="memory")
    # Use reduce if it exists and is not None, otherwise use original dims
    target_dims = selected_config.reduce if (hasattr(selected_config, 'reduce') and selected_config.reduce is not None) else dims
    
    # Create schema using object attributes (not dictionary access)
    svs_schema = {
        "index": {
            "name": "test_svs_index",
            "prefix": "test:svs:",
        },
        "fields": [
            {"name": "movie_id", "type": "tag"},
            {"name": "title", "type": "text"},
            {
                "name": "embedding",
                "type": "vector",
                "attrs": {
                    "dims": target_dims,
                    "algorithm": "svs-vamana",
                    "datatype": selected_config.datatype,  # Object attribute access
                    "distance_metric": "cosine"
                }
            }
        ]
    }
    
    print(f"✅ SVS schema created successfully")
    print(f"   Index name: test_svs_index")
    print(f"   Dimensions: {target_dims}")
    print(f"   Datatype: {selected_config.datatype}")
    
    # Try to create the index
    svs_index = SearchIndex.from_dict(svs_schema, redis_url=REDIS_URL)
    svs_index.create(overwrite=True)
    print(f"✅ SVS index created successfully in Redis")
    
    # Cleanup
    svs_index.delete()
    print(f"✅ Test index cleaned up")
    
except Exception as e:
    print(f"❌ SVS index creation failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Summary
print("\n" + "=" * 70)
print("🎉 ALL TESTS PASSED!")
print("=" * 70)
print("\nThe migration notebooks should work correctly:")
print("  ✅ All imports working")
print("  ✅ Redis connection established")
print("  ✅ SVS-VAMANA support detected")
print("  ✅ Sample data loaded")
print("  ✅ CompressionAdvisor API fixed (object attributes)")
print("  ✅ HFTextVectorizer working")
print("  ✅ Embedding generation successful")
print("  ✅ SVS index creation with config object working")
print("\n✅ Notebooks are ready to run!")

