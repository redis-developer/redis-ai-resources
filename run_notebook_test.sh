#!/bin/bash

# Test script to run key cells from the migration notebooks
# This simulates what would happen in Colab/Jupyter

echo "=========================================="
echo "Testing Migration Notebooks"
echo "=========================================="
echo ""

# Check if Redis is running
echo "1. Checking Redis connection..."
if docker ps | grep -q redis; then
    echo "✅ Redis container is running"
else
    echo "❌ Redis container not found"
    echo "Starting Redis Stack..."
    docker run -d --name redis-stack-test -p 6379:6379 redis/redis-stack:latest
    sleep 5
fi

# Test Redis connection with Python
echo ""
echo "2. Testing Redis connection with Python..."
python3 -c "
import sys
try:
    import redis
    client = redis.Redis(host='localhost', port=6379)
    result = client.ping()
    print(f'✅ Redis ping: {result}')
except ImportError:
    print('❌ redis-py not installed')
    print('Install with: pip install redis')
    sys.exit(1)
except Exception as e:
    print(f'❌ Redis connection failed: {e}')
    sys.exit(1)
"

if [ $? -ne 0 ]; then
    echo "Redis connection test failed"
    exit 1
fi

# Test RedisVL imports
echo ""
echo "3. Testing RedisVL imports..."
python3 -c "
import sys
try:
    from redisvl.index import SearchIndex
    from redisvl.query import VectorQuery
    from redisvl.redis.utils import array_to_buffer, buffer_to_array
    from redisvl.utils import CompressionAdvisor
    from redisvl.redis.connection import supports_svs
    print('✅ RedisVL imports successful')
except ImportError as e:
    print(f'❌ RedisVL import failed: {e}')
    print('Install with: pip install git+https://github.com/redis/redis-vl-python.git')
    sys.exit(1)
"

if [ $? -ne 0 ]; then
    echo "RedisVL import test failed"
    exit 1
fi

# Test HFTextVectorizer
echo ""
echo "4. Testing HFTextVectorizer..."
python3 -c "
import sys
try:
    from redisvl.utils.vectorize import HFTextVectorizer
    print('✅ HFTextVectorizer import successful')
    
    # Try to initialize (this will fail if sentence-transformers is missing)
    try:
        vectorizer = HFTextVectorizer(
            model='sentence-transformers/all-mpnet-base-v2',
            dims=768
        )
        print('✅ HFTextVectorizer initialization successful')
    except ImportError as e:
        print(f'⚠️  HFTextVectorizer requires sentence-transformers: {e}')
        print('Install with: pip install sentence-transformers')
        sys.exit(2)
        
except ImportError as e:
    print(f'❌ HFTextVectorizer import failed: {e}')
    sys.exit(1)
"

VECTORIZER_STATUS=$?
if [ $VECTORIZER_STATUS -eq 2 ]; then
    echo "⚠️  sentence-transformers is required but not installed"
elif [ $VECTORIZER_STATUS -ne 0 ]; then
    echo "HFTextVectorizer test failed"
    exit 1
fi

# Test SVS support
echo ""
echo "5. Testing SVS-VAMANA support..."
python3 -c "
import redis
from redisvl.redis.connection import supports_svs

client = redis.Redis(host='localhost', port=6379)
svs_supported = supports_svs(client)
print(f'SVS-VAMANA support: {svs_supported}')

if svs_supported:
    print('✅ SVS-VAMANA is supported')
else:
    print('⚠️  SVS-VAMANA not supported (requires Redis Stack 8.2.0+ with RediSearch 2.8.10+)')
"

# Test numpy
echo ""
echo "6. Testing numpy..."
python3 -c "
import sys
try:
    import numpy as np
    print(f'✅ numpy version: {np.__version__}')
except ImportError:
    print('❌ numpy not installed')
    print('Install with: pip install numpy')
    sys.exit(1)
"

if [ $? -ne 0 ]; then
    echo "numpy test failed"
    exit 1
fi

# Summary
echo ""
echo "=========================================="
echo "Test Summary"
echo "=========================================="
echo "✅ Redis connection: OK"
echo "✅ RedisVL imports: OK"
echo "✅ numpy: OK"

if [ $VECTORIZER_STATUS -eq 0 ]; then
    echo "✅ HFTextVectorizer: OK"
else
    echo "⚠️  HFTextVectorizer: Requires sentence-transformers"
fi

echo ""
echo "To run the notebooks successfully, ensure all dependencies are installed:"
echo "  pip install git+https://github.com/redis/redis-vl-python.git redis>=6.4.0 numpy>=1.21.0 sentence-transformers>=2.2.0"
echo ""

