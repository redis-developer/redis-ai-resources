**Index Configuration Breakdown:**

#### Index Settings:
```python
"index": {
    "name": "movies",  # Index identifier
    "prefix": "movies",  # All keys: movies:*, movies:1, movies:2...
    "storage_type": "hash"  # Hash or JSON
}
```

**Storage Types Deep Dive:**

**HASH vs JSON - What Are They?**

**1. Redis Hash:**
```python
# Hash is like a dictionary/map inside Redis
# key → {field1: value1, field2: value2, ...}

# Example storage:
HSET movies:1 title "Inception"
HSET movies:1 genre "action"
HSET movies:1 rating 9
HSET movies:1 vector <binary_data>

# View hash:
HGETALL movies:1
# Output:
# {
#   "title": "Inception",
#   "genre": "action",
#   "rating": "9",
#   "vector": b"\x9ef|=..."
# }

# Characteristics:
# - Flat structure (no nesting)
# - All values stored as strings (except binary)
# - Fast operations: O(1) for field access
# - Compact memory representation
```

**2. RedisJSON:**
```python
# JSON is native JSON document storage
# key → {nested: {json: "structure"}}

# Example storage:
JSON.SET movies:1 $ '{
  "title": "Inception",
  "genre": "action",
  "rating": 9,
  "metadata": {
    "director": "Christopher Nolan",
    "year": 2010,
    "tags": ["sci-fi", "thriller"]
  },
  "vector": [0.123, -0.456, ...]
}'

# Query with JSONPath:
JSON.GET movies:1 $.metadata.director
# Output: "Christopher Nolan"

# Characteristics:
# - Supports nested structures
# - Native JSON types (numbers, booleans, arrays)
# - JSONPath queries
# - Slightly more memory overhead
```

**Hash vs JSON Performance:**
```python
# Hash (faster):
# - Simpler data structure
# - Less parsing overhead
# - ~10-20% faster for simple key-value
# - Memory: ~50-100 bytes overhead per hash

# JSON (more flexible):
# - Complex nested data
# - Array operations
# - Atomic updates to nested fields
# - Memory: ~100-200 bytes overhead per document

# Recommendation:
# Use Hash for: Simple flat data (our movies example)
# Use JSON for: Complex nested structures, arrays
```

**Why Hash is Faster:**
```python
# Hash: Direct field access
# 1. Hash table lookup: O(1)
# 2. Return value: O(1)
# Total: O(1)

# JSON: Parse + navigate
# 1. Retrieve JSON string: O(1)
# 2. Parse JSON: O(n) where n = document size
# 3. Navigate JSONPath: O(m) where m = path depth
# Total: O(n + m)

# For simple data, hash avoids parsing overhead

# Benchmark example:
import time

# Hash access
start = time.time()
for i in range(10000):
    client.hget(f"movies:{i}", "title")
hash_time = time.time() - start
print(f"Hash: {hash_time:.3f}s")  # ~0.5s

# JSON access
start = time.time()
for i in range(10000):
    client.json().get(f"movies_json:{i}", "$.title")
json_time = time.time() - start
print(f"JSON: {json_time:.3f}s")  # ~0.6-0.7s

# Hash is ~20% faster for simple access
```

**When to Use Each:**
```python
# Use Hash when:
# ✓ Flat data structure
# ✓ Maximum performance needed
# ✓ Simple field access patterns
# ✓ Vectors + simple metadata

# Use JSON when:
# ✓ Nested data (user.address.city)
# ✓ Arrays ([tags, categories])
# ✓ Need JSONPath queries
# ✓ Complex document structures
# ✓ Atomic updates to nested fields
```

#### Field Types in RedisVL:

RedisVL supports multiple field types for building searchable indices:

##### 1. **TEXT** (Full-Text Search)
```python
{
    "name": "title",
    "type": "text",
    "attrs": {
        "weight": 2.0,  # Boost importance in scoring
        "sortable": False,  # Can't sort by text (use tag/numeric)
        "no_stem": False,  # Enable stemming (run→running)
        "no_index": False,  # Actually index this field
        "phonetic": "dm:en"  # Phonetic matching (optional)
    }
}
```

**Use TEXT for:**
- Article content
- Product descriptions  
- User comments
- Any natural language text that needs fuzzy/full-text search

**Search capabilities:**
- Tokenization and stemming
- Phrase matching
- Fuzzy matching
- BM25 scoring
- Stopword removal

**Example:**
```python
# Field definition
{"name": "description", "type": "text"}

# Search query
Text("description") % "action packed superhero"
# Finds: "action-packed superhero movie"
#        "packed with superhero action"
#        "actions by superheroes" (stemmed)
```

##### 2. **TAG** (Exact Match, Categories)
```python
{
    "name": "genre",
    "type": "tag",
    "attrs": {
        "separator": ",",  # For multi-value tags: "action,thriller"
        "sortable": True,  # Enable sorting
        "case_sensitive": False  # Case-insensitive matching
    }
}
```

**Use TAG for:**
- Categories (genre, department)
- Status flags (active, pending, completed)
- IDs (user_id, product_sku)
- Enum values
- Multiple values per field (comma-separated)

**Search capabilities:**
- Exact match only (no tokenization)
- Very fast lookups
- Multi-value support

**Example:**
```python
# Field definition
{"name": "genre", "type": "tag"}

# Storage
{"genre": "action,thriller"}  # Multiple tags

# Search queries
Tag("genre") == "action"  # Matches
Tag("genre") == "thriller"  # Also matches
Tag("genre") == ["action", "comedy"]  # OR logic
Tag("genre") != "horror"  # Exclude
```

##### 3. **NUMERIC** (Range Queries, Sorting)
```python
{
    "name": "rating",
    "type": "numeric",
    "attrs": {
        "sortable": True,  # Enable sorting
        "no_index": False  # Index for range queries
    }
}
```

**Use NUMERIC for:**
- Ratings/scores
- Prices
- Timestamps (as Unix epoch)
- Counts/quantities
- Any filterable number

**Search capabilities:**
- Range queries (>, <, >=, <=)
- Exact match (==)
- Sorting

**Example:**
```python
# Field definition
{"name": "price", "type": "numeric"}

# Search queries
Num("price") <= 100  # Under $100
Num("price") >= 50 & Num("price") <= 150  # $50-$150 range
Num("rating") >= 4.5  # High rated
```

##### 4. **VECTOR** (Semantic Search)
```python
{
    "name": "vector",
    "type": "vector",
    "attrs": {
        "dims": 384,  # Vector dimensions (MUST match model!)
        "distance_metric": "cosine",  # cosine, l2, ip
        "algorithm": "flat",  # flat, hnsw, svs-vamana
        "datatype": "float32",  # float32, float64, float16
        "initial_cap": 1000  # Initial capacity (HNSW)
    }
}
```

**Use VECTOR for:**
- Text embeddings
- Image embeddings
- Audio embeddings
- Any semantic similarity search

**Search capabilities:**
- KNN (K-Nearest Neighbors)
- Range queries (within threshold)
- Hybrid search (with filters)

**Example:**
```python
# Field definition
{"name": "embedding", "type": "vector", "attrs": {"dims": 384, ...}}

# Search query
VectorQuery(
    vector=query_embedding,  # Must be 384 dims
    vector_field_name="embedding"
)
```

##### 5. **GEO** (Location-Based Search)
```python
{
    "name": "location",
    "type": "geo",
    "attrs": {
        "sortable": False  # Geo fields can't be sorted
    }
}
```

**Use GEO for:**
-# RedisVL Vector Search Workshop - Comprehensive Guide

## Table of Contents
1. [Introduction](#introduction)
2. [Cell-by-Cell Walkthrough](#cell-by-cell-walkthrough)
3. [Technical Q&A](#technical-qa)
4. [Architecture & Performance](#architecture--performance)
5. [Production Considerations](#production-considerations)

---

## Introduction

### What is Vector Search?
Vector search (also called semantic search or similarity search) enables finding similar items based on meaning rather than exact keyword matches. It works by:
1. Converting data (text, images, audio) into numerical vectors (embeddings)
2. Storing these vectors in a specialized database
3. Finding similar items by measuring distance between vectors

### What is Redis?

**Redis Core (Open Source)** provides fundamental data structures:
- **Strings**: Simple key-value pairs
- **Lists**: Ordered collections (queues, stacks)
- **Sets**: Unordered unique collections
- **Sorted Sets**: Sets with scores for ranking
- **Hashes**: Field-value pairs (like Python dicts)
- **Streams**: Append-only log structures
- **Bitmaps**: Bit-level operations
- **HyperLogLog**: Probabilistic cardinality counting
- **Geospatial**: Location-based queries

**Redis Stack** adds powerful modules on top of Redis Core:
- **RediSearch**: Full-text search, vector search, aggregations
- **RedisJSON**: Native JSON document storage with JSONPath queries
- **RedisTimeSeries**: Time-series data structures
- **RedisBloom**: Probabilistic data structures (Bloom filters, Cuckoo filters)
- **RedisGraph**: Graph database capabilities (deprecated in favor of other solutions)

**For this workshop**, we need **RediSearch** for vector similarity search capabilities.

### Why Redis?
- **Speed**: Sub-millisecond query latency
- **Versatility**: Cache, database, and message broker in one
- **Real-time**: Immediate indexing without rebuild delays
- **Hybrid capabilities**: Combines vector search with traditional filters
- **Proven scale**: Used by Fortune 500 companies for decades

---

## Cell-by-Cell Walkthrough

### CELL 1: Title and Introduction (Markdown)
```markdown
![Redis](https://redis.io/wp-content/uploads/2024/04/Logotype.svg?auto=webp&quality=85,75&width=120)
# Vector Search with RedisVL
```

**Workshop Notes:**
- This notebook demonstrates building a semantic movie search engine
- Vector search is foundational for modern AI: RAG, recommendations, semantic search
- Redis Stack provides vector database capabilities with cache-level performance
- RedisVL abstracts complexity, making vector operations simple

**Key Points to Emphasize:**
- Vector databases are the backbone of GenAI applications
- This is a hands-on introduction - by the end, attendees will build working vector search
- The techniques learned apply to any domain: e-commerce, documentation, media, etc.

---

### CELL 2: Prepare Data (Markdown)

**Workshop Notes:**
- Using 20 movies dataset - small enough to understand, large enough to be meaningful
- Each movie has structured metadata (title, rating, genre) and unstructured text (description)
- **The key insight**: We'll convert descriptions to vectors to enable semantic search

**Why Movies?**
- Relatable domain everyone understands
- Rich descriptions showcase semantic similarity well
- Genre/rating demonstrate hybrid filtering

---

### CELL 3: Download Dataset (Code)
```bash
!git clone https://github.com/redis-developer/redis-ai-resources.git temp_repo
!mv temp_repo/python-recipes/vector-search/resources .
!rm -rf temp_repo
```

**What's Happening:**
1. Clone Redis AI resources repository
2. Extract just the `/resources` folder containing `movies.json`
3. Clean up temporary files

**Workshop Notes:**
- Only needed in Colab/cloud environments
- Local users: data is already in the repository
- In production: load from your database, API, or file system
- The JSON contains our 20 movies with descriptions

**Common Question:** "What format should my data be in?"
- Any format works: JSON, CSV, database, API
- Key requirement: structured format that pandas can load
- Need fields for: searchable text + metadata for filtering

---

### CELL 4: Packages Header (Markdown)

**Workshop Notes:**
- About to install Python dependencies
- All packages are production-ready and actively maintained

---

### CELL 5: Install Dependencies (Code)
```python
%pip install -q "redisvl>=0.6.0" sentence-transformers pandas nltk
```

**Package Breakdown:**

#### 1. **redisvl** (Redis Vector Library) ≥0.6.0
- **Purpose**: High-level Python client for Redis vector operations
- **Built on**: redis-py (standard Redis Python client)
- **Key Features**:
  - Declarative schema definition (YAML or Python dict)
  - Multiple query types (Vector, Range, Hybrid, Text)
  - Built-in vectorizers (OpenAI, Cohere, HuggingFace, etc.)
  - Semantic caching for LLM applications
  - CLI tools for index management

**Why not plain redis-py?**
- redis-py requires manual query construction with complex syntax
- RedisVL provides Pythonic abstractions and best practices
- Handles serialization, batching, error handling automatically

#### 2. **sentence-transformers**
- **Purpose**: Create text embeddings using pre-trained models
- **Provider**: Hugging Face
- **Model Used**: `all-MiniLM-L6-v2`
  - Dimensions: 384
  - Speed: Fast inference (~2000 sentences/sec on CPU)
  - Quality: Good for general purpose semantic similarity
  - Training: 1B+ sentence pairs

**Alternatives:**
- OpenAI `text-embedding-ada-002` (1536 dims, requires API key)
- Cohere embeddings (1024-4096 dims, requires API key)
- Custom models fine-tuned for your domain

#### 3. **pandas**
- **Purpose**: Data manipulation and analysis
- **Use Cases**: 
  - Loading JSON/CSV datasets
  - Data transformation and cleaning
  - Displaying search results in tabular format

#### 4. **nltk** (Natural Language Toolkit)
- **Purpose**: NLP utilities, specifically stopwords
- **Stopwords**: Common words with little semantic value ("the", "a", "is", "and")
- **Use Case**: Improve text search quality by filtering noise

**Installation Note:**
- `-q` flag suppresses verbose output
- In production, pin exact versions: `redisvl==0.6.0`
- Total install size: ~500MB (mostly sentence-transformers models)

---

### CELL 6: Install Redis Stack Header (Markdown)

**Workshop Notes:**
- Redis Stack = Redis Open Source + modules
- Required modules: **RediSearch** (vector search), **RedisJSON** (JSON storage)

---

### CELL 7: Install Redis Stack - Colab (Code)
```bash
%%sh
curl -fsSL https://packages.redis.io/gpg | sudo gpg --dearmor -o /usr/share/keyrings/redis-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/redis-archive-keyring.gpg] https://packages.redis.io/deb $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/redis.list
sudo apt-get update  > /dev/null 2>&1
sudo apt-get install redis-stack-server  > /dev/null 2>&1
redis-stack-server --daemonize yes
```

**What's Happening:**
1. Add Redis GPG key for package verification
2. Add Redis repository to apt sources
3. Update package lists
4. Install Redis Stack Server
5. Start Redis as background daemon

**Workshop Notes:**
- This installs Redis Stack 7.2+ with all modules
- `--daemonize yes`: runs in background (doesn't block terminal)
- Colab-specific - not needed for local development

**Why Redis Stack vs Redis Open Source?**
- Open Source: Core data structures only
- Stack: Includes Search, JSON, Time Series, Bloom filters
- Enterprise: Stack + high availability, active-active geo-replication

---

### CELL 8: Alternative Installation Methods (Markdown)

**Workshop Notes:**

#### Option 1: Redis Cloud (Recommended for Production Testing)
```bash
# Free tier: 30MB RAM, perfect for learning
# Sign up: https://redis.com/try-free/
```
- Fully managed, no infrastructure
- Automatic scaling and backups
- SSL/TLS by default

#### Option 2: Docker (Best for Local Development)
```bash
docker run -d --name redis-stack-server -p 6379:6379 redis/redis-stack-server:latest
```
- Isolated environment
- Easy cleanup: `docker rm -f redis-stack-server`
- Consistent across team members

#### Option 3: OS-Specific Install
```bash
# macOS
brew install redis-stack

# Ubuntu/Debian
sudo apt install redis-stack-server

# Windows
# Use WSL2 + Docker or Redis Cloud
```

**Common Question:** "Which should I use?"
- **Learning**: Docker or Colab
- **Development**: Docker
- **Production**: Redis Cloud or Redis Enterprise

---

### CELL 9: Redis Connection Setup (Code)
```python
import os
import warnings

warnings.filterwarnings('ignore')

# Replace values below with your own if using Redis Cloud instance
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = os.getenv("REDIS_PORT", "6379")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")

# If SSL is enabled on the endpoint, use rediss:// as the URL prefix
REDIS_URL = f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}"
```

**Connection String Format:**
```
redis://[username]:[password]@[host]:[port]/[database]
rediss://[username]:[password]@[host]:[port]/[database]  # SSL/TLS
```

**Workshop Notes:**
- Follows 12-factor app methodology (environment variables for config)
- Defaults to local development: `localhost:6379`
- Password optional for local (required for production)
- `rediss://` (double 's') for SSL/TLS connections

**For Redis Cloud:**
```python
# Example Redis Cloud settings
REDIS_HOST = "redis-12345.c123.us-east-1-1.ec2.cloud.redislabs.com"
REDIS_PORT = "12345"
REDIS_PASSWORD = "your-strong-password-here"
```

**Security Best Practices:**
- Never hardcode credentials in notebooks/code
- Use environment variables or secrets manager
- Enable SSL/TLS for production
- Use strong passwords (20+ characters)
- Rotate credentials regularly

---

### CELL 10: Create Redis Client (Code)
```python
from redis import Redis

client = Redis.from_url(REDIS_URL)
client.ping()
```

**What's Happening:**
1. Import redis-py client library
2. Create client connection from URL
3. `ping()` verifies connection (returns `True` if successful)

**Workshop Notes:**
- This is standard redis-py client (not RedisVL yet)
- RedisVL will use this client internally
- `ping()` is best practice for connection verification

**Troubleshooting:**
```python
# If ping() fails, check:
try:
    result = client.ping()
    print(f"✓ Connected to Redis: {result}")
except redis.ConnectionError as e:
    print(f"✗ Connection failed: {e}")
    print("Troubleshooting:")
    print("1. Is Redis running? (ps aux | grep redis)")
    print("2. Check host/port/password")
    print("3. Firewall blocking port 6379?")
```

**Common Question:** "What if I have multiple Redis instances?"
```python
# You can create multiple clients
cache_client = Redis.from_url("redis://localhost:6379/0")  # DB 0 for cache
vector_client = Redis.from_url("redis://localhost:6379/1")  # DB 1 for vectors
```

---

### CELL 11: Check Redis Info (Code)
```python
client.info()
```

**What's Happening:**
- `INFO` command returns server statistics dictionary
- Contains ~100+ metrics about Redis server state

**Key Sections to Review:**

#### Server Info:
- `redis_version`: Should be 7.2+ for optimal vector search
- `redis_mode`: "standalone" or "cluster"
- `os`: Operating system

#### Memory:
- `used_memory_human`: Current memory usage
- `maxmemory`: Memory limit (0 = no limit)
- `maxmemory_policy`: What happens when limit reached

#### Modules (Most Important):
```python
modules = client.info()['modules']
for module in modules:
    print(f"{module['name']}: v{module['ver']}")
# Expected output:
# search: v80205  ← RediSearch for vector search
# ReJSON: v80201  ← JSON document support
# timeseries: v80200
# bf: v80203  ← Bloom filters
```

**Workshop Notes:**
- If `modules` section is missing, you're not using Redis Stack!
- `search` module provides vector search capabilities
- Version numbers: 80205 = 8.2.05

**Diagnostic Commands:**
```python
# Check specific info sections
print(client.info('server'))
print(client.info('memory'))
print(client.info('modules'))
```

---

### CELL 12: Optional Flush (Code)
```python
#client.flushall()
```

**What's Happening:**
- `flushall()` deletes ALL data from ALL databases
- Commented out by default (good practice!)

**Workshop Notes:**
- ⚠️ **DANGER**: This is destructive and irreversible
- Only uncomment for development/testing
- Never run in production without explicit confirmation

**Safer Alternatives:**
```python
# Delete only keys matching pattern
for key in client.scan_iter("movies:*"):
    client.delete(key)

# Delete specific index
index.delete()  # Removes index, keeps data

# Delete index AND data
index.delete(drop=True)  # Removes index and all associated data
```

---

### CELL 13: Load Movies Dataset Header (Markdown)

**Workshop Notes:**
- About to load and inspect our sample data
- This is a typical data loading pattern for any ML/AI project

---

### CELL 14: Load Data with Pandas (Code)
```python
import pandas as pd
import numpy as np
import json

df = pd.read_json("resources/movies.json")
print("Loaded", len(df), "movie entries")

df.head()
```

**What's Happening:**
1. Load JSON file into pandas DataFrame
2. Print row count (20 movies)
3. Display first 5 rows with `head()`

**Data Structure:**
```
Columns:
- id (int): Unique identifier (1-20)
- title (str): Movie name
- genre (str): "action" or "comedy"
- rating (int): Quality score 6-10
- description (str): Plot summary (this gets vectorized!)
```

**Workshop Notes:**
- Real applications have thousands/millions of documents
- Dataset intentionally small for learning
- Descriptions are 1-2 sentences (ideal for embeddings)

**Data Quality Matters:**
```python
# Check for issues
print(f"Missing values:\n{df.isnull().sum()}")
print(f"\nDescription length stats:\n{df['description'].str.len().describe()}")
print(f"\nUnique genres: {df['genre'].unique()}")
```

**Example Movies:**
- "Explosive Pursuit" (Action, 7): "A daring cop chases a notorious criminal..."
- "Skyfall" (Action, 8): "James Bond returns to track down a dangerous network..."

**Common Question:** "What if my descriptions are very long?"
- Truncate to model's max tokens (512 for many models)
- Or chunk into multiple vectors
- Or use models designed for long documents (Longformer, etc.)

---

### CELL 15: Initialize Vectorizer (Code)
```python
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
```

**Theoretical Background - Embeddings:**

An **embedding** is a dense vector representation that captures semantic meaning:
```
"The cat sat on the mat" → [0.234, -0.123, 0.456, ..., 0.789]  # 384 numbers
"A feline was on the rug" → [0.229, -0.119, 0.451, ..., 0.782]  # Similar vector!
"Python programming" → [-0.678, 0.234, -0.123, ..., 0.456]  # Different vector
```

**Key Properties:**
- Similar meanings → similar vectors (measured by distance metrics)
- Enables semantic search without keyword matching
- Captures context, synonyms, and relationships

**Model Choice: `all-MiniLM-L6-v2`**
```
Specifications:
- Architecture: MiniLM (distilled from BERT)
- Dimensions: 384 (good balance of quality vs size)
- Max sequence: 256 tokens
- Training: 1B+ sentence pairs (SNLI, MultiNLI, etc.)
- Speed: ~2000 sentences/sec on CPU
- Size: ~80MB download
```

**Why this model?**
- ✅ Good quality for general purpose
- ✅ Fast inference (no GPU needed)
- ✅ Free (no API keys)
- ✅ Runs locally (data privacy)

**Alternative Models:**
```python
# OpenAI (requires API key, $$)
from redisvl.utils.vectorize import OpenAITextVectorizer
openai_vectorizer = OpenAITextVectorizer(
    model="text-embedding-ada-002",  # 1536 dims
    api_key=os.getenv("OPENAI_API_KEY")
)

# Cohere (requires API key)
from redisvl.utils.vectorize import CohereTextVectorizer
cohere_vectorizer = CohereTextVectorizer(
    model="embed-english-v3.0",
    api_key=os.getenv("COHERE_API_KEY")
)

# Custom Hugging Face model
hf_large = HFTextVectorizer(
    model="sentence-transformers/all-mpnet-base-v2"  # 768 dims, slower but better
)
```

**Embedding Cache - Deep Dive:**

**What is the Embedding Cache?**
The `EmbeddingsCache` is a Redis-based caching layer that stores previously computed embeddings to avoid redundant computation.

**Why is it needed?**
```python
# Without cache:
text = "The quick brown fox"
embedding1 = model.encode(text)  # Takes ~50-100ms (compute intensive)
embedding2 = model.encode(text)  # Takes ~50-100ms again (wasteful!)

# With cache:
text = "The quick brown fox"
embedding1 = hf.embed(text)  # First call: ~50-100ms (computes + caches)
embedding2 = hf.embed(text)  # Second call: ~1ms (from cache, 50-100x faster!)
```

**How it works:**
```python
cache=EmbeddingsCache(
    name="embedcache",  # Redis key prefix for cache entries
    ttl=600,  # Time-to-live: 10 minutes (600 seconds)
    redis_client=client,  # Uses same Redis instance
)

# Internal cache behavior:
# 1. Input text is hashed: hash("your text") → "abc123def456"
# 2. Check Redis: GET embedcache:abc123def456
# 3. If exists: Return cached embedding (fast!)
# 4. If not exists: 
#    a. Compute embedding (slow)
#    b. Store in Redis: SETEX embedcache:abc123def456 600 <embedding_bytes>
#    c. Return computed embedding
```

**Cache Storage in Redis:**
```python
# Cache entries are stored as Redis strings
key = f"embedcache:{hash(text)}"
value = serialized_embedding_bytes

# View cache entries:
for key in client.scan_iter("embedcache:*"):
    print(key)
# Output:
# b'embedcache:a1b2c3d4e5f6'
# b'embedcache:1a2b3c4d5e6f'
# ...
```

**TTL (Time-To-Live) Explained:**
```python
ttl=600  # Cache expires after 10 minutes

# Why expire?
# 1. Prevent stale data if embeddings change
# 2. Manage memory usage (old embeddings are removed)
# 3. Balance between performance and freshness

# TTL recommendations:
ttl=3600      # 1 hour - for stable production data
ttl=86400     # 24 hours - for rarely changing data
ttl=300       # 5 minutes - for frequently updating data
ttl=None      # Never expire - for static datasets (careful with memory!)
```

**Performance Impact:**
```python
import time

# Measure with cache
times_with_cache = []
for _ in range(100):
    start = time.time()
    vec = hf.embed("sample text")
    times_with_cache.append(time.time() - start)

print(f"First call (no cache): {times_with_cache[0]*1000:.2f}ms")  # ~50-100ms
print(f"Subsequent calls (cached): {np.mean(times_with_cache[1:])*1000:.2f}ms")  # ~1ms

# Cache hit rate
# 50-100x speedup for repeated queries!
```

**Cache Memory Usage:**
```python
# Each cached embedding uses memory:
# Hash key: ~64 bytes
# Embedding: 384 dims × 4 bytes = 1,536 bytes
# Redis overhead: ~64 bytes
# Total per entry: ~1,664 bytes ≈ 1.6 KB

# For 10,000 cached embeddings:
# 10,000 × 1.6 KB = 16 MB (negligible!)

# Cache is much smaller than full index
```

**Production Considerations:**
```python
# Monitor cache hit rate
hits = 0
misses = 0

def embed_with_monitoring(text):
    cache_key = f"embedcache:{hash(text)}"
    if client.exists(cache_key):
        hits += 1
    else:
        misses += 1
    return hf.embed(text)

# Target: >80% hit rate for good performance
hit_rate = hits / (hits + misses)
print(f"Cache hit rate: {hit_rate*100:.1f}%")
```

**Workshop Notes:**
- `TOKENIZERS_PARALLELISM=false` prevents threading warnings
- Cache automatically manages expiration
- In production, increase TTL or use persistent cache
- Cache is shared across all vectorizer instances using same Redis client

---

### CELL 16: Generate Embeddings (Code)
```python
df["vector"] = hf.embed_many(df["description"].tolist(), as_buffer=True)

df.head()
```

**What's Happening:**
1. Extract all descriptions as list: `["desc1", "desc2", ...]`
2. `embed_many()` batch processes all descriptions
3. `as_buffer=True` returns bytes (Redis-compatible format)
4. Store vectors in new DataFrame column

**Why `as_buffer=True`? (Binary vs Numeric Storage)**

**The Problem with Numeric Storage:**
```python
# Without as_buffer (returns numpy array)
vector_array = hf.embed("text")  # np.array([0.123, -0.456, 0.789, ...])
type(vector_array)  # <class 'numpy.ndarray'>

# Storing as array in Redis requires serialization:
import pickle
vector_serialized = pickle.dumps(vector_array)
# Or JSON (very inefficient):
vector_json = json.dumps(vector_array.tolist())

# Problems:
# 1. Pickle adds overhead (metadata, versioning info)
# 2. JSON is text-based, huge size (each float as string)
# 3. Not optimized for Redis vector search
```

**With Binary Storage (`as_buffer=True`):**
```python
# With as_buffer (returns raw bytes)
vector_bytes = hf.embed("text", as_buffer=True)  
type(vector_bytes)  # <class 'bytes'>

# Example:
# b'\x9e\x66\x7c\x3d\x67\x60\x0a\x3b...'

# This is raw IEEE 754 float32 representation
# Each float32 = 4 bytes
# 384 dimensions × 4 bytes = 1,536 bytes total

# Benefits:
# 1. Compact: No serialization overhead
# 2. Fast: Direct binary format Redis understands
# 3. Native: Redis vector search expects this format
# 4. Efficient: 4 bytes per dimension (optimal for float32)
```

**Binary Format Explanation:**
```python
# How float32 is stored as bytes:
import struct
import numpy as np

# Single float
value = 0.123456
bytes_repr = struct.pack('f', value)  # 'f' = float32
print(bytes_repr)  # b'w\xbe\xfc='

# Array of floats (what embeddings are)
array = np.array([0.123, -0.456, 0.789], dtype=np.float32)
bytes_repr = array.tobytes()
print(bytes_repr)  # b'{\x14\xfb>\x9a\x99\xe9\xbf\xc3\xf5I?'

# This is what gets stored in Redis!
```

**Storage Size Comparison:**
```python
import sys
import json
import pickle
import numpy as np

vec = np.random.rand(384).astype(np.float32)

# Method 1: Raw bytes (as_buffer=True) ✅ BEST
bytes_size = len(vec.tobytes())
print(f"Bytes: {bytes_size} bytes")  # 1,536 bytes

# Method 2: Pickle
pickle_size = len(pickle.dumps(vec))
print(f"Pickle: {pickle_size} bytes")  # ~1,700 bytes (+10% overhead)

# Method 3: JSON ❌ WORST
json_size = len(json.dumps(vec.tolist()))
print(f"JSON: {json_size} bytes")  # ~6,000 bytes (4x larger!)

# For 1 million vectors:
# Bytes: 1.5 GB
# Pickle: 1.65 GB
# JSON: 6 GB (waste 4.5 GB!)
```

**Why Redis Vector Search Requires Bytes:**
```python
# Redis RediSearch module expects binary format
# When you query, Redis:
# 1. Reads raw bytes from memory
# 2. Interprets as float32 array
# 3. Computes distance (no deserialization!)

# With JSON/Pickle:
# 1. Read serialized data
# 2. Deserialize to numbers (SLOW!)
# 3. Compute distance
# = Much slower, more CPU, more memory

# Binary format = Zero-copy, direct math operations
```

**Converting Between Formats:**
```python
# Bytes → NumPy array (for inspection)
vec_bytes = df.iloc[0]['vector']
vec_array = np.frombuffer(vec_bytes, dtype=np.float32)
print(f"Dimensions: {len(vec_array)}")  # 384
print(f"First 5 values: {vec_array[:5]}")
# [-0.0234, 0.1234, -0.5678, 0.9012, ...]

# NumPy array → Bytes (for storage)
vec_array = np.array([0.1, 0.2, 0.3], dtype=np.float32)
vec_bytes = vec_array.tobytes()
client.hset("key", "vector", vec_bytes)
```

**Batch Processing Benefits:**
```python
# Bad (slow): One at a time
for desc in descriptions:
    vec = hf.embed(desc)  # 20 separate calls

# Good (fast): Batch processing
vectors = hf.embed_many(descriptions)  # 1 batched call

# Why faster?
# 1. Model processes multiple texts in parallel
# 2. GPU utilization better (if using GPU)
# 3. Reduced Python/model overhead
# 4. Typical speedup: 2-5x for batches of 10-100
```

**Workshop Notes:**
- This step takes 5-30 seconds depending on hardware
- Progress: Watch for model loading messages
- Cache prevents re-computation if you re-run
- Vectors displayed as bytes: `b'\x9ef|=...'` (not human-readable, that's OK)
- **Key takeaway**: Binary storage is compact, fast, and what Redis expects

**Common Question:** "Can I use float64 instead of float32?"
```python
# Yes, but usually not worth it:
attrs = {
    "datatype": "float64"  # 8 bytes per dimension
}

# Doubles storage: 384 × 8 = 3,072 bytes per vector
# Minimal accuracy gain for most applications
# Recommendation: Stick with float32 unless you have specific precision requirements
```

---

### CELL 17: Define Redis Index Schema Header (Markdown)

**Workshop Notes:**
- Schema defines how data is structured and indexed in Redis
- Like creating a database table, but for vectors + metadata
- RedisVL provides declarative schema definition

---

### CELL 18: Create Index Schema (Code)
```python
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
```

**Index Configuration Breakdown:**

#### Index Settings:
```python
"index": {
    "name": "movies",  # Index identifier
    "prefix": "movies",  # All keys: movies:*, movies:1, movies:2...
    "storage_type": "hash"  # Hash or JSON
}
```

**Storage Types:**
- **Hash**: Key-value pairs, efficient, limited nesting
- **JSON**: Nested structures, JSONPath queries, slightly slower

#### Field Types:

##### 1. **TEXT** (Full-Text Search)
```python
{
    "name": "title",
    "type": "text",
}
```
- Tokenized for full-text search
- Supports stemming (run → running → ran)
- Phrase matching, fuzzy search
- Use for: descriptions, articles, comments

##### 2. **TAG** (Exact Match)
```python
{
    "name": "genre",
    "type": "tag",
    "attrs": {"sortable": True}
}
```
- Exact match only (no tokenization)
- Efficient for categories, enums
- Supports multiple values: "action,adventure"
- Use for: categories, status, types

##### 3. **NUMERIC** (Range Queries)
```python
{
    "name": "rating",
    "type": "numeric",
    "attrs": {"sortable": True}
}
```
- Range queries: `rating >= 7`, `1000 < price < 5000`
- Sorting by value
- Use for: prices, scores, timestamps, counts

##### 4. **VECTOR** (Semantic Search)
```python
{
    "name": "vector",
    "type": "vector",
    "attrs": {
        "dims": 384,  # Must match embedding model!
        "distance_metric": "cosine",
        "algorithm": "flat",
        "datatype": "float32"
    }
}
```

**Vector Configuration Deep Dive:**

##### Distance Metrics:
```python
# 1. COSINE (recommended for text)
distance_metric = "cosine"
# Measures angle between vectors
# Range: 0 to 2 (lower = more similar)
# Normalized: ignores vector magnitude
# Use: Text, normalized data
```

**Cosine Formula:**
```
cosine_distance = 1 - (A · B) / (||A|| × ||B||)

Where:
- A · B = dot product
- ||A|| = magnitude of A
```

```python
# 2. EUCLIDEAN (L2)
distance_metric = "l2"
# Measures straight-line distance
# Range: 0 to ∞ (lower = more similar)
# Sensitive to magnitude
# Use: Images, spatial data
```

**Euclidean Formula:**
```
l2_distance = √Σ(Ai - Bi)²
```

```python
# 3. INNER PRODUCT (IP)
distance_metric = "ip"
# Dot product (assumes normalized vectors)
# Range: -∞ to ∞ (higher = more similar)
# Fastest to compute
# Use: Pre-normalized embeddings
```

##### Indexing Algorithms:

```python
# 1. FLAT (exact search)
algorithm = "flat"
# Pros:
# - 100% accuracy (exact results)
# - Simple, no tuning needed
# Cons:
# - Slow on large datasets (checks every vector)
# - O(N) complexity
# Use: <100K vectors or when accuracy critical
```

```python
# 2. HNSW (approximate search)
algorithm = "hnsw"
attrs = {
    "m": 16,  # Connections per node (higher = better accuracy, more memory)
    "ef_construction": 200,  # Build-time accuracy (higher = better quality index)
    "ef_runtime": 10  # Query-time accuracy (higher = more accurate, slower)
}
# Pros:
# - Very fast (10-100x faster than FLAT)
# - Sub-linear query time
# - Good accuracy (95-99%)
# Cons:
# - More memory usage
# - Tuning required
# Use: >100K vectors, speed critical
```

**HNSW Parameters Explained:**
- `m`: Graph connectivity (16-64 typical, default 16)
- `ef_construction`: Higher = better index quality (100-500 typical)
- `ef_runtime`: Trade-off accuracy vs speed (10-200 typical)

```python
# 3. SVS-VAMANA (Intel optimized, Redis 8.2+)
algorithm = "svs-vamana"
attrs = {
    "graph_max_degree": 40,
    "construction_window_size": 250,
    "compression": "lvq8"  # 8-bit compression
}
# Pros:
# - Excellent speed
# - Low memory (compression)
# - Intel CPU optimized
# Cons:
# - Redis 8.2+ only
# - Less battle-tested than HNSW
# Use: Large-scale, Intel hardware
```

##### Data Types:
```python
datatype = "float32"  # Standard (4 bytes per dimension)
datatype = "float64"  # Higher precision (8 bytes, rarely needed)
datatype = "float16"  # Lower precision (2 bytes, experimental)
```

**Memory Calculation:**
```
Vector memory per document = dimensions × bytes_per_dim
384 × 4 bytes = 1,536 bytes = 1.5 KB per vector

For 1 million vectors:
1,000,000 × 1.5 KB = 1.5 GB just for vectors
```

**Create Index:**
```python
index = SearchIndex(schema, client)
index.create(overwrite=True, drop=True)
```

**Parameters:**
- `overwrite=True`: Delete existing index with same name
- `drop=True`: Also delete all data

**Workshop Notes:**
- Schema can also be defined in YAML (better for version control)
- `dims=384` must match your embedding model!
- Start with FLAT, migrate to HNSW when you have >100K vectors
- Cosine is safest default for text embeddings

**YAML Schema Alternative:**
```yaml
# schema.yaml
version: '0.1.0'
index:
  name: movies
  prefix: movies
  storage_type: hash

fields:
  - name: title
    type: text
  - name: genre
    type: tag
    attrs:
      sortable: true
  - name: rating
    type: numeric
    attrs:
      sortable: true
  - name: vector
    type: vector
    attrs:
      dims: 384
      distance_metric: cosine
      algorithm: flat
      datatype: float32
```

```python
# Load from YAML
schema = IndexSchema.from_yaml("schema.yaml")
```

---

### CELL 19: Inspect Index via CLI (Code)
```bash
!rvl index info -i movies -u {REDIS_URL}
```

**What's Happening:**
- `rvl` = RedisVL command-line interface
- Shows index metadata in formatted tables

**Workshop Notes:**
- CLI tool useful for debugging and operations
- Verify configuration matches expectations
- Check field types, dimensions, algorithms

**CLI Output Explained:**
```
Index Information:
┌─────────────┬──────────────┬──────────┬───────────────┬──────────┐
│ Index Name  │ Storage Type │ Prefixes │ Index Options │ Indexing │
├─────────────┼──────────────┼──────────┼───────────────┼──────────┤
│ movies      │ HASH         │ [movies] │ []            │ 0        │
└─────────────┴──────────────┴──────────┴───────────────┴──────────┘
```
- `Indexing: 0` = no documents indexed yet

**Other CLI Commands:**
```bash
# List all indices
!rvl index listall -u {REDIS_URL}

# Delete index
!rvl index delete -i movies -u {REDIS_URL}

# Create from YAML
!rvl index create -s schema.yaml -u {REDIS_URL}

# Get statistics
!rvl stats -i movies -u {REDIS_URL}
```

---

### CELL 20: Populate Index Header (Markdown)

**Workshop Notes:**
- Time to load our movie data into Redis
- This makes data searchable

---

### CELL 21: Load Data (Code)
```python
index.load(df.to_dict(orient="records"))
```

**What's Happening:**
1. `df.to_dict(orient="records")` converts DataFrame to list of dicts:
```python
[
    {"id": 1, "title": "Explosive Pursuit", "genre": "action", ...},
    {"id": 2, "title": "Skyfall", "genre": "action", ...},
    ...
]
```
2. `index.load()` performs batch insert
3. Returns list of generated Redis keys

**Output Example:**
```python
[
    'movies:01K7T4BMAEZMNPYTV73KZFYN3R',  # ULID format
    'movies:01K7T4BMAE21PEY7NSDDQN4195',
    ...
]
```

**Key Generation:**
- RedisVL auto-generates ULIDs (Universally Unique Lexicographically Sortable IDs)
- Format: `{prefix}:{ulid}`
- ULIDs are time-ordered (can sort chronologically)

**Workshop Notes:**
- Batch insert is efficient (~1000-10000 inserts/sec)
- Data is immediately searchable (real-time indexing)
- No need to "rebuild" index like traditional search engines

**Behind the Scenes:**
```python
# What RedisVL does internally
for record in data:
    key = f"{prefix}:{generate_ulid()}"
    client.hset(key, mapping=record)  # Store as hash
    # Index updates automatically
```

**Verify Loading:**
```python
# Check document count
info = index.info()
print(f"Documents indexed: {info['num_docs']}")  # Should be 20

# Inspect a record
keys = client.keys("movies:*")
sample_key = keys[0]
sample_data = client.hgetall(sample_key)
print(sample_data)
```

---

### CELL 22: Search Techniques Header (Markdown)

**Workshop Notes:**
- Now for the exciting part - searching!
- We'll explore different search patterns and their use cases

---

### CELL 23: Standard Vector Search (Code)
```python
from redisvl.query import VectorQuery

user_query = "High tech and action packed movie"

embedded_user_query = hf.embed(user_query)

vec_query = VectorQuery(
    vector=embedded_user_query,
    vector_field_name="vector",
    num_results=3,
    return_fields=["title", "genre"],
    return_score=True,
)

result = index.query(vec_query)
pd.DataFrame(result)
```

**Theoretical Background - K-Nearest Neighbors (KNN):**

KNN finds the K closest vectors to a query vector:
```
Query: "High tech action"
     ↓ (embed)
Vector: [0.12, -0.45, 0.78, ...]
     ↓ (search)
Compare distance to all stored vectors
     ↓
Return top K closest matches
```

**Distance Calculation (Cosine):**
```python
# For each document vector:
similarity = 1 - cosine_similarity(query_vec, doc_vec)

# Lower distance = more similar
# Range: 0 (identical) to 2 (opposite)
```

**Results Interpretation:**
```
                                  id  vector_distance              title   genre
0  movies:01K7T4BMAEAJZJZEA2S05V2G5H    0.64973795414   Fast & Furious 9  action
1  movies:01K7T4BMAE7ZKS3N3DVBQ1WCCF   0.763235211372  Mad Max: Fury Road action
2  movies:01K7T4BMAEPMDQF1FVRV3Y60JF   0.792449593544      The Lego Movie comedy
```

**Why These Results?**
1. **Fast & Furious 9** (0.649 distance):
   - Description mentions "high-tech", "face off"
   - Semantically closest to "high tech action packed"

2. **Mad Max** (0.763 distance):
   - Action-heavy, chase sequences
   - Less tech-focused but still relevant

3. **The Lego Movie** (0.792 distance):
   - Has action elements
   - Farther semantically (comedy, not tech)

**Workshop Notes:**
- **Key Insight**: No keyword matching! Pure semantic understanding
- Query never said "Fast & Furious" but found it through meaning
- This is the power of vector search
- Notice Comedy movies can appear if semantically similar

**Common Question:** "How do I choose K (num_results)?"
```python
# Recommendations:
num_results = 5   # Product search (show few options)
num_results = 20  # RAG (retrieve context for LLM)
num_results = 100 # Reranking (get candidates for 2-stage retrieval)
```

**Performance:**
```python
import time
start = time.time()
result = index.query(vec_query)
print(f"Query time: {(time.time()-start)*1000:.2f}ms")
# Typical: 1-10ms for FLAT, <1ms for HNSW
```

---

### CELL 24: Vector Search with Filters Header (Markdown)

**Workshop Notes:**
- Combining semantic search with structured filters
- This is where Redis shines - hybrid search capabilities

---

### CELL 25: Filter by Genre Header (Markdown)

**Workshop Notes:**
- Constraining search to specific category

---

### CELL 26: Tag Filter (Code)
```python
from redisvl.query.filter import Tag

tag_filter = Tag("genre") == "action"

vec_query.set_filter(tag_filter)

result = index.query(vec_query)
pd.DataFrame(result)
```

**What's Happening:**
1. Create tag filter: `genre == "action"`
2. Apply to existing query
3. Redis pre-filters to action movies BEFORE vector comparison

**Filter Execution Order:**
```
1. Apply tag filter → Filter to action movies (10 out of 20)
2. Compute vector distances → Only on filtered set
3. Return top K → From filtered results
```

**Results:**
```
                                  id  vector_distance               title   genre
0  movies:01K7T4BMAEAJZJZEA2S05V2G5H    0.64973795414    Fast & Furious 9  action
1  movies:01K7T4BMAE7ZKS3N3DVBQ1WCCF   0.763235211372  Mad Max: Fury Road  action
2  movies:01K7T4BMAEZMNPYTV73KZFYN3R   0.796153008938   Explosive Pursuit  action
```

**Workshop Notes:**
- All results now action genre (no comedy)
- "The Lego Movie" excluded despite semantic relevance
- Real use case: "Find Python books" (semantic + category filter)

**Tag Filter Operators:**
```python
# Equality
Tag("genre") == "action"

# Inequality
Tag("genre") != "comedy"

# Multiple values (OR logic)
Tag("genre") == ["action", "thriller"]  # action OR thriller

# Field existence
Tag("genre").exists()
```

**Performance Impact:**
- Pre-filtering is very efficient (uses Redis sorted sets)
- Can filter millions of records in milliseconds
- Then vector search only on filtered subset

---

### CELL 27: Multiple Filters Header (Markdown)

**Workshop Notes:**
- Combining multiple conditions with AND/OR logic

---

### CELL 28: Combined Filters (Code)
```python
from redisvl.query.filter import Num

# Build combined filter expressions
tag_filter = Tag("genre") == "action"
num_filter = Num("rating") >= 7
combined_filter = tag_filter & num_filter

# Build vector query
vec_query = VectorQuery(
    vector=embedded_user_query,
    vector_field_name="vector",
    num_results=3,
    return_fields=["title", "rating", "genre"],
    return_score=True,
    filter_expression=combined_filter
)

result = index.query(vec_query)
pd.DataFrame(result)
```

**Filter Logic:**
```python
# AND operator (&)
filter1 & filter2  # Both conditions must be true

# OR operator (|)
filter1 | filter2  # Either condition can be true

# NOT operator (~)
~filter1  # Inverts condition

# Complex expressions
(Tag("genre") == "action") & (Num("rating") >= 7) | (Tag("featured") == "yes")
# (action AND rating>=7) OR featured
```

**Numeric Filter Operators:**
```python
# Comparison operators
Num("rating") == 8      # Exact match
Num("rating") != 8      # Not equal
Num("rating") > 7       # Greater than
Num("rating") >= 7      # Greater or equal
Num("rating") < 9       # Less than
Num("rating") <= 9      # Less or equal

# Range queries
Num("rating") >= 7 & Num("rating") <= 9  # Between 7 and 9

# Or simplified
(Num("price") >= 100) & (Num("price") <= 500)  # $100-$500 range
```

**Results:**
```
                                  id  vector_distance               title rating  genre
0  movies:01K7T4BMAE7ZKS3N3DVBQ1WCCF   0.763235211372  Mad Max: Fury Road      8  action
1  movies:01K7T4BMAEZMNPYTV73KZFYN3R   0.796153008938   Explosive Pursuit      7  action
2  movies:01K7T4BMAEYWEZS72634ZFS303   0.876494169235           Inception      9  action
```

**Workshop Notes:**
- Now filtering by TWO conditions: action AND rating ≥7
- More restrictive = fewer results but higher quality
- Real e-commerce example: "Find Nike shoes, size 10, under $150, in stock"

**Complex E-commerce Filter Example:**
```python
from redisvl.query.filter import Tag, Num, Text

product_filter = (
    (Tag("brand") == "nike") &
    (Tag("size") == "10") &
    (Num("price") <= 150) &
    (Tag("in_stock") == "yes") &
    (Num("rating") >= 4.0)
)

product_query = VectorQuery(
    vector=user_preference_embedding,  # User's style preference
    vector_field_name="style_vector",
    num_results=10,
    filter_expression=product_filter
)
```

---

### CELL 29: Full-Text Search Filter Header (Markdown)

**Workshop Notes:**
- Searching for specific phrases within text fields

---

### CELL 30: Text Filter (Code)
```python
from redisvl.query.filter import Text

text_filter = Text("description") % "criminal mastermind"

vec_query = VectorQuery(
    vector=embedded_user_query,
    vector_field_name="vector",
    num_results=3,
    return_fields=["title", "rating", "genre", "description"],
    return_score=True,
    filter_expression=text_filter
)

result = index.query(vec_query)
pd.DataFrame(result)
```

**Text Search Operators:**
```python
# Phrase match (words must appear together)
Text("description") % "criminal mastermind"

# Word match (any order, stemmed)
Text("description") == "criminal mastermind"  # Matches "criminals" or "masterminds"

# Multiple words (OR logic)
Text("description") % "hero | villain"  # hero OR villain

# Multiple words (AND logic)
Text("description") % "hero villain"  # Both must appear

# Negation
Text("description") % "hero -villain"  # hero but NOT villain
```

**Tokenization Example:**
```
Input: "The criminal mastermind plans the heist"
Tokens: [criminal, mastermind, plan, heist]  # Stopwords removed, stemmed
```

**Results:**
```
                                  id  vector_distance            title rating   genre
0  movies:01K7T4BMAE6KW01NKAVS2HSHYP   0.827253937721    Despicable Me      7  comedy
1  movies:01K7T4BMAE9E3H8180KZ7JMV3W   0.990856587887  The Dark Knight      9  action
```

**Why These Results?**
- Both have exact phrase "criminal mastermind" in description
- Ranked by semantic similarity to query
- Shows diversity: comedy + action

**Workshop Notes:**
- Use case: "Find docs containing 'GDPR compliance' that match this query"
- Combines keyword precision with semantic ranking
- More specific than pure vector search

**Stemming Example:**
```python
# These all match the same stem:
"criminal" → "crimin"
"criminals" → "crimin"
"criminality" → "crimin"

# Search for "criminal" finds all variants
```

---

### CELL 31: Wildcard Text Match Header (Markdown)

**Workshop Notes:**
- Using wildcards for flexible pattern matching

---

### CELL 32: Wildcard Filter (Code)
```python
text_filter = Text("description") % "crim*"

vec_query = VectorQuery(
    vector=embedded_user_query,
    vector_field_name="vector",
    num_results=3,
    return_fields=["title", "rating", "genre", "description"],
    return_score=True,
    filter_expression=text_filter
)

result = index.query(vec_query)
pd.DataFrame(result)
```

**Wildcard Patterns:**
```python
# Suffix wildcard
Text("field") % "test*"  # Matches: test, tests, testing, tester

# Prefix wildcard
Text("field") % "*tion"  # Matches: action, mention, creation

# Middle wildcard
Text("field") % "t*st"   # Matches: test, toast, trust

# Multiple wildcards
Text("field") % "c*m*l"  # Matches: camel, criminal, commercial
```

**Results:**
```
                                  id  vector_distance               title rating  genre
0  movies:01K7T4BMAEZMNPYTV73KZFYN3R   0.796153008938   Explosive Pursuit      7  action
1  movies:01K7T4BMAEPQZ10JTTGZS0JW68   0.807471394539     The Incredibles      8  comedy
2  movies:01K7T4BMAE6KW01NKAVS2HSHYP   0.827253937721       Despicable Me      7  comedy
```

**Why More Results?**
- "crim*" matches: criminal, crime, criminals, etc.
- Broader than exact phrase match
- 3 results instead of 2

**Workshop Notes:**
- Useful when you know the root but not exact form
- Be careful with very short patterns (too many matches)
- Example: "tech*" might match: tech, technical, technology, technician

**Performance Note:**
```python
# Efficient wildcards (start with letters)
"comp*"   # Good: Narrows search space quickly

# Inefficient wildcards (start with *)
"*puter"  # Bad: Must check all terms
```

---

### CELL 33: Fuzzy Match Header (Markdown)

**Workshop Notes:**
- Handling typos and slight variations using Levenshtein distance

---

### CELL 34: Fuzzy Filter (Code)
```python
text_filter = Text("description") % "%hero%"

vec_query = VectorQuery(
    vector=embedded_user_query,
    vector_field_name="vector",
    num_results=3,
    return_fields=["title", "rating", "genre", "description"],
    return_score=True,
    filter_expression=text_filter
)

result = index.query(vec_query)
pd.DataFrame(result)
```

**Fuzzy Matching:**
```python
# Syntax: %term% allows 1 character edit distance
Text("field") % "%hero%"

# What it matches:
"hero"   ✓ Exact match
"heros"  ✓ 1 insertion
"her"    ✓ 1 deletion
"hera"   ✓ 1 substitution
"heroes" ✗ 2+ edits (too far)
```

**Levenshtein Distance Formula:**
```
Distance = minimum edits (insert/delete/substitute) to transform A → B

Examples:
"hero" → "her"   = 1 (delete 'o')
"hero" → "zero"  = 1 (substitute 'h' with 'z')
"hero" → "heron" = 1 (insert 'n')
```

**Workshop Notes:**
- Handles typos automatically
- **Warning**: Can produce unexpected matches with short words
  - "%he%" might match: he, her, hex, hue, hen, etc.
- Use minimum 4-5 characters for fuzzy matching

**Results:**
```
                                  id  vector_distance                 title rating  genre
0  movies:01K7T4BMAEVCZCA7Z2R3Y837S6   0.889985799789           Black Widow      7  action
1  movies:01K7T4BMAE0XHHQ5W08WWXYNTV    0.89386677742          The Avengers      8  action
2  movies:01K7T4BMAETZ6H2MVQSVY4E46W   0.943198144436  The Princess Diaries      6  comedy
```

**Fuzzy Matching Pitfalls:**
```python
# Be careful with short terms
Text("name") % "%jo%"
# Matches: jo, joe, john, joy, job, jon, jot, joan...

# Better: Use longer terms or exact match
Text("name") == "john"  # Exact with stemming
Text("name") % "john*"  # Wildcard prefix
```

**Real Use Case:**
```python
# User search with typo correction
user_input = "iphone"  # User meant "iPhone"
query_filter = Text("product_name") % f"%{user_input}%"
# Matches: iPhone, iphone, iphne (1 typo), etc.
```

---

### CELL 35: Range Queries Header (Markdown)

**Workshop Notes:**
- Finding all vectors within a similarity threshold
- Different from KNN (which always returns K results)

---

### CELL 36: Range Query (Code)
```python
from redisvl.query import RangeQuery

user_query = "Family friendly fantasy movies"

embedded_user_query = hf.embed(user_query)

range_query = RangeQuery(
    vector=embedded_user_query,
    vector_field_name="vector",
    return_fields=["title", "rating", "genre"],
    return_score=True,
    distance_threshold=0.8  # find all items with distance < 0.8
)

result = index.query(range_query)
pd.DataFrame(result)
```

**Range Query vs KNN:**
```python
# KNN (K-Nearest Neighbors)
VectorQuery(num_results=5)
# Always returns exactly 5 results (or fewer if dataset smaller)
# Returns: [most similar, 2nd, 3rd, 4th, 5th]

# Range Query
RangeQuery(distance_threshold=0.8)
# Returns ALL results with distance < 0.8
# Could be 0 results, could be 1000 results
# Variable number based on threshold
```

**Distance Threshold Selection:**
```
Cosine Distance Scale:
0.0 ────────── 0.5 ────────── 1.0 ────────── 1.5 ────────── 2.0
│              │              │              │              │
Identical   Very Close    Related     Somewhat    Completely
                                      Related     Different

Typical Thresholds:
0.3 - Very strict (near-duplicates)
0.5 - Strict (highly relevant)
0.7 - Moderate (relevant)
0.8 - Loose (somewhat relevant)  ← Used in example
1.0 - Very loose (barely relevant)
```

**Results:**
```
                                  id  vector_distance            title rating  genre
0  movies:01K7T4BMAEPQZ10JTTGZS0JW68   0.644702553749  The Incredibles      8  comedy
1  movies:01K7T4BMAEVCZCA7Z2R3Y837S6   0.747986972332      Black Widow      7  action
2  movies:01K7T4BMAE6KW01NKAVS2HSHYP   0.750915408134    Despicable Me      7  comedy
3  movies:01K7T4BMAEVV6R6B2M22QFV7DW   0.751298904419            Shrek      8  comedy
4  movies:01K7T4BMAE8PR91YXEHRH3APYP   0.761669397354   Monsters, Inc.      8  comedy
5  movies:01K7T4BMAED0S8Z02DN2SYQR1H   0.778580188751          Aladdin      8  comedy
```

**Workshop Notes:**
- 6 results returned (all under 0.8 distance)
- KNN would return exactly 3 (with num_results=3)
- Use case: "Show ALL similar products" or "Find ALL relevant documents"

**Choosing Range vs KNN:**
```python
# Use KNN when:
# - You want top N results always
# - Pagination (show 10 per page)
# - Fixed UI slots (show 5 recommendations)

# Use Range when:
# - Quality threshold matters more than quantity
# - "Show everything that matches well enough"
# - Duplicate detection (distance < 0.1)
# - Clustering (find all neighbors within radius)
```

**Tuning Threshold:**
```python
# Start conservative, then relax
thresholds = [0.5, 0.6, 0.7, 0.8, 0.9]

for threshold in thresholds:
    query = RangeQuery(vector=vec, distance_threshold=threshold)
    results = index.query(query)
    print(f"Threshold {threshold}: {len(results)} results")

# Output:
# Threshold 0.5: 2 results  (very strict)
# Threshold 0.6: 5 results
# Threshold 0.7: 12 results
# Threshold 0.8: 25 results (used in example)
# Threshold 0.9: 50 results (very loose)
```

---

### CELL 37: Range with Filters Header (Markdown)

**Workshop Notes:**
- Combining range queries with structured filters

---

### CELL 38: Filtered Range Query (Code)
```python
range_query = RangeQuery(
    vector=embedded_user_query,
    vector_field_name="vector",
    return_fields=["title", "rating", "genre"],
    distance_threshold=0.8
)

numeric_filter = Num("rating") >= 8

range_query.set_filter(numeric_filter)

result = index.query(range_query)
pd.DataFrame(result)
```

**Filter Execution Flow:**
```
1. Apply numeric filter → Only rating >= 8 movies
2. Compute distances → Only on filtered set
3. Apply threshold → Only results with distance < 0.8
4. Return results → Ordered by distance
```

**Results:**
```
                                  id  vector_distance            title rating  genre
0  movies:01K7T4BMAEPQZ10JTTGZS0JW68   0.644702553749  The Incredibles      8  comedy
1  movies:01K7T4BMAEVV6R6B2M22QFV7DW   0.751298904419            Shrek      8  comedy
2  movies:01K7T4BMAE8PR91YXEHRH3APYP   0.761669397354   Monsters, Inc.      8  comedy
3  movies:01K7T4BMAED0S8Z02DN2SYQR1H   0.778580188751          Aladdin      8  comedy
```

**Workshop Notes:**
- Now only 4 results (down from 6)
- Removed movies with rating 7 (Black Widow, Despicable Me)
- Real use case: "Find all hotels within 5km AND rating ≥ 4 stars"

**Complex Range Filter Example:**
```python
# E-commerce: Find all relevant products in stock under $100
range_query = RangeQuery(
    vector=product_preference_vec,
    distance_threshold=0.7,
    filter_expression=(
        (Tag("in_stock") == "yes") &
        (Num("price") <= 100) &
        (Num("rating") >= 4.0)
    )
)
```

---

### CELL 39: Full-Text Search Header (Markdown)

**Workshop Notes:**
- Traditional text search WITHOUT vectors
- Uses BM25 algorithm for ranking

---

### CELL 40: TextQuery with BM25 (Code)
```python
from redisvl.query import TextQuery

user_query = "das High tech, action packed, superheros mit fight scenes"

text_query = TextQuery(
    text=user_query,
    text_field_name="description",
    text_scorer="BM25STD",  # or "BM25" or "TFIDF"
    num_results=20,
    return_fields=["title", "description"],
    stopwords="german"
)

result = index.query(text_query)[:4]
pd.DataFrame(result)[["title", "score"]]
```

**BM25 Algorithm (Best Match 25):**

BM25 is a probabilistic ranking function that considers:
1. **Term Frequency (TF)**: How often term appears in document
2. **Inverse Document Frequency (IDF)**: How rare term is across all documents
3. **Document Length**: Normalizes for document size

**Formula:**
```
score(D,Q) = Σ IDF(qi) × (f(qi,D) × (k1+1)) / (f(qi,D) + k1 × (1-b+b×|D|/avgdl))

Where:
- D = document
- Q = query
- qi = query term i
- f(qi,D) = frequency of qi in D
- |D| = length of D
- avgdl = average document length
- k1 = term saturation parameter (usually 1.2-2.0)
- b = length normalization (usually 0.75)
```

**BM25 vs TF-IDF:**
```python
# TF-IDF (older)
score = TF × IDF
# Linear growth with term frequency

# BM25 (better)
score = IDF × (TF with saturation)
# Diminishing returns after multiple occurrences
```

**Stopwords Processing:**
```python
# Input query
"das High tech, action packed, superheros mit fight scenes"

# German stopwords removed
"das" → removed
"mit" → removed

# Final processed query
"high tech action packed superheros fight scenes"
```

**Results:**
```
              title     score
0  Fast & Furious 9  5.376819  # Highest: has "high tech", "action", "packed"
1   The Incredibles  3.537206  # Medium: has "superheros" variant, "fight"
2 Explosive Pursuit  2.454928  # Lower: has "action"
3         Toy Story  1.459313  # Lowest: weak match
```

**Workshop Notes:**
- This is pure keyword/term matching (NO vectors!)
- Different from vector search - finds exact/stemmed words
- Useful when users search with specific terms
- Works across languages with proper stopwords

**Text Scorer Options:**
```python
# BM25 (recommended)
text_scorer="BM25"  # Standard BM25

# BM25 Standard (more tuning)
text_scorer="BM25STD"  # With additional normalization

# TF-IDF (older, simpler)
text_scorer="TFIDF"  # Classic information retrieval
```

**When to Use Text Search vs Vector Search:**
```python
# Use Text Search when:
# - Users search with specific keywords/product codes
# - Exact term matching important (legal, medical)
# - Fast keyword lookups needed

# Use Vector Search when:
# - Understanding meaning/intent matters
# - Handling synonyms/paraphrasing
# - Cross-lingual search
# - Recommendation systems

# Use Hybrid (next cell) when:
# - Best of both worlds (usually best choice!)
```

---

### CELL 41: Check Query String (Code)
```python
text_query.query_string()
```

**Output:**
```
'@description:(high | tech | action | packed | superheros | fight | scenes)'
```

**Query Syntax Breakdown:**
```
@description:              # Search in description field
(term1 | term2 | term3)   # OR logic (any term matches)
```

**Workshop Notes:**
- Shows internal Redis query syntax
- Stopwords ("das", "mit") removed automatically
- Terms joined with OR operator
- This is what actually gets sent to Redis

**Redis Query Syntax Examples:**
```python
# AND logic
"@description:(hero & villain)"  # Both must appear

# OR logic
"@description:(hero | villain)"  # Either can appear

# NOT logic
"@description:(hero -villain)"   # hero but NOT villain

# Phrase match
'@description:"criminal mastermind"'  # Exact phrase

# Field-specific
"@title:(batman) @description:(joker)"  # batman in title, joker in description
```

---

### CELL 42: Hybrid Search Header (Markdown)

**Workshop Notes:**
- **THE BEST APPROACH**: Combines semantic + keyword matching
- Industry best practice for highest quality results
- Used by modern search engines (Google, Bing, etc.)

---

### CELL 43: Hybrid Query (Code)
```python
from redisvl.query import HybridQuery

user_query = "das High tech, action packed, superheros mit fight scenes"

hybrid_query = HybridQuery(
    text=user_query,
    text_field_name="description",
    text_scorer="BM25",
    vector=embedded_user_query,
    vector_field_name="vector",
    alpha=0.7,  # 70% vector, 30% text
    num_results=20,
    return_fields=["title", "description"],
    stopwords="german"
)

result = index.query(hybrid_query)[:4]
pd.DataFrame(result)[["title", "vector_similarity", "text_score", "hybrid_score"]]
```

**Hybrid Search Architecture:**
```
User Query: "high tech action superheros"
     │
     ├─→ Text Search Path (BM25)
     │   ├─ Tokenize & remove stopwords
     │   ├─ Match keywords in text
     │   └─ Score: text_score
     │
     ├─→ Vector Search Path (KNN)
     │   ├─ Generate embedding
     │   ├─ Compute cosine distances
     │   └─ Score: vector_similarity
     │
     └─→ Combine Scores
         hybrid_score = α × vector_sim + (1-α) × text_score
```

**Alpha Parameter (α):**
```
α = 0.0  → Pure text search (100% keywords)
α = 0.3  → Mostly text (70% text, 30% semantic)
α = 0.5  → Balanced (50/50)
α = 0.7  → Mostly semantic (70% vector, 30% text)  ← Recommended default
α = 1.0  → Pure vector search (100% semantic)
```

**Score Normalization:**
```python
# Vector distances need normalization to [0,1] range
vector_similarity = (2 - cosine_distance) / 2  # Cosine: [0,2] → [0,1]
# Higher = more similar

# Text scores already normalized via BM25
text_score = bm25_score / max_possible_score  # → [0,1]

# Combine
hybrid_score = 0.7 × vector_similarity + 0.3 × text_score
```

**Results:**
```
             title  vector_similarity  text_score  hybrid_score
0  The Incredibles         0.677648723  0.683368580    0.679364680
1 Fast & Furious 9         0.537397742  0.498220622    0.525644606
2        Toy Story         0.553009659  0.213523123    0.451163698
3      Black Widow         0.626006513  0.000000000    0.438204559
```

**Analysis of Results:**

**1. The Incredibles (Winner - 0.679 hybrid score):**
- Strong vector similarity (0.678): Semantically about superheroes/action
- Strong text score (0.683): Contains keywords "superheros", "fight"
- **Best of both worlds** - relevant semantically AND has keywords

**2. Fast & Furious 9 (0.526):**
- Medium vector similarity (0.537): Action-packed theme
- Medium text score (0.498): Has "high tech", "action", "packed"
- Balanced match

**3. Toy Story (0.451):**
- Medium vector similarity (0.553): Has action elements
- Weak text score (0.214): Few matching keywords
- Vector search keeps it relevant despite weak text match

**4. Black Widow (0.438):**
- Good vector similarity (0.626): Superhero action movie
- Zero text score (0.000): No matching keywords in description
- Pure semantic match - wouldn't rank high in text-only search

**Workshop Notes:**
- **Key Insight**: Hybrid search combines strengths, avoids weaknesses
  - Catches exact keyword matches (text search strength)
  - Understands meaning and synonyms (vector search strength)
  - Handles typos better (vector) while respecting important terms (text)

**Tuning Alpha for Your Use Case:**
```python
# E-commerce product search
alpha = 0.5  # Balanced - users search with brand names (text) but also browse (semantic)

# Documentation/knowledge base
alpha = 0.7  # Favor semantic - users phrase questions differently

# Code search
alpha = 0.3  # Favor text - exact function/variable names matter

# Academic papers
alpha = 0.8  # Favor semantic - concepts matter more than exact terms

# Legal/medical
alpha = 0.2  # Favor text - specific terminology crucial
```

**A/B Testing Alpha:**
```python
# Test different alphas, measure metrics
alphas = [0.3, 0.5, 0.7, 0.9]

for alpha in alphas:
    query = HybridQuery(text=q, vector=v, alpha=alpha)
    results = index.query(query)
    
    # Measure: CTR, time-to-click, relevance ratings, etc.
    metrics = evaluate_results(results, ground_truth)
    print(f"Alpha {alpha}: Precision={metrics.precision}, Recall={metrics.recall}")
```

**Real-World Hybrid Search Example:**
```python
# Airbnb-style search
user_query = "cozy mountain cabin with fireplace near skiing"
query_vector = embedder.embed(user_query)

hybrid_query = HybridQuery(
    text=user_query,
    text_field_name="description",
    vector=query_vector,
    vector_field_name="listing_embedding",
    alpha=0.6,  # Slightly favor semantic
    filter_expression=(
        (Tag("property_type") == "cabin") &
        (Num("price_per_night") <= 200) &
        (Tag("amenities") == "fireplace") &
        (Num("distance_to_ski") <= 10)  # km
    ),
    num_results=50
)
```

---

### CELL 44: Display NLTK Stopwords (Code)
```python
import nltk
from nltk.corpus import stopwords
nltk.download('stopwords', quiet=True)

deutch_stopwords = stopwords.words('german')
english_stopwords = stopwords.words('english')

print(f"Number of German stopwords: {len(deutch_stopwords)}\nGerman stopwords: {deutch_stopwords}\n\nNumber of English stopwords: {len(english_stopwords)}\nEnglish stopwords: {english_stopwords}")
```

**Theoretical Background - Stopwords:**

**What are stopwords?**
- High-frequency, low-information words
- Provide grammatical structure but little semantic meaning
- Removing them improves search quality and performance

**German Stopwords (232):**
```
Common examples:
- Articles: der, die, das, ein, eine
- Prepositions: mit, in, auf, an, von
- Conjunctions: und, oder, aber
- Pronouns: ich, du, er, sie, es
```

**English Stopwords (198):**
```
Common examples:
- Articles: the, a, an
- Prepositions: in, on, at, to, from
- Conjunctions: and, or, but
- Pronouns: I, you, he, she, it
- Auxiliaries: is, are, was, were, have, has
```

**Why Remove Stopwords?**
```
Query: "the best italian restaurant in the city"
Without stopword removal:
- "the" appears everywhere (not discriminative)
- "in" appears everywhere (not discriminative)
After stopword removal:
- "best italian restaurant city" (content words only)
- More focused, better results
```

**Workshop Notes:**
- NLTK provides stopword lists for 16+ languages
- Custom stopwords can be added for domain-specific terms
- Vector search naturally handles stopwords (they get low weights)
- Text search benefits more from explicit stopword removal

**Custom Stopwords Example:**
```python
# Domain-specific stopwords
medical_stopwords = english_stopwords + [
    "patient", "doctor", "hospital",  # Common but not discriminative
    "reported", "showed", "indicated"
]

# Remove domain-common terms that don't help search
tech_stopwords = english_stopwords + [
    "application", "system", "software",
    "user", "data", "information"
]
```

**Important Stopwords to Keep:**
```python
# Sometimes stopwords matter!

# Negations (critical meaning)
keep = ["not", "no", "never", "neither", "nor"]
# "working" vs "not working" - huge difference!

# Medical context
keep = ["over", "under", "above", "below"]
# "over 100mg" vs "under 100mg" - critical!

# Programming
keep = ["and", "or", "not"]
# Boolean operators are keywords!
```

**RedisVL Stopwords Configuration:**
```python
# Use language-specific stopwords
TextQuery(text=query, stopwords="english")
TextQuery(text=query, stopwords="german")
TextQuery(text=query, stopwords="french")

# Use custom stopwords
custom_stops = ["custom", "domain", "terms"]
TextQuery(text=query, stopwords=custom_stops)

# No stopword removal
TextQuery(text=query, stopwords=None)
```

---

### CELL 45: Next Steps Header (Markdown)

**Workshop Notes:**
- Link to advanced RedisVL documentation
- Encourages further exploration
- Points to additional resources

**Additional Resources to Mention:**
```
1. RedisVL GitHub: https://github.com/redis/redis-vl-python
2. Redis AI Resources: https://github.com/redis-developer/redis-ai-resources
3. Redis Documentation: https://redis.io/docs/stack/search/
4. RedisVL Docs: https://www.redisvl.com/
5. Redis University: https://university.redis.com/
```

---

### CELL 46: Cleanup (Code)
```python
index.delete()
```

**What's Happening:**
- Removes the index structure from Redis
- Data remains in Redis (only index deleted)

**Workshop Notes:**
- Good practice for demo/test cleanup
- In production, manage index lifecycle carefully

**Cleanup Options:**
```python
# 1. Delete index only (keep data)
index.delete()  # or index.delete(drop=False)
# Use case: Re-indexing with different schema

# 2. Delete index AND data
index.delete(drop=True)
# Use case: Complete cleanup

# 3. Keep index, delete some data
for key in client.scan_iter("movies:*"):
    if should_delete(key):
        client.delete(key)

# 4. Flush everything (DANGER!)
# client.flushall()  # Never in production!
```

**Re-indexing Pattern:**
```python
# Safe re-indexing without downtime
old_index = SearchIndex(old_schema, client)
new_index = SearchIndex(new_schema, client)

# 1. Create new index with different name
new_index.create()

# 2. Load data into new index
new_index.load(data)

# 3. Verify new index
assert new_index.info()['num_docs'] > 0

# 4. Switch application to new index
# (Update config/environment variable)

# 5. Delete old index
old_index.delete(drop=True)
```

---

## Technical Q&A

### General Vector Search Questions

**Q: How do embeddings capture meaning?**
A: Embeddings are learned through training on massive datasets. The model learns that:
- Words appearing in similar contexts should have similar vectors
- Synonyms cluster together in vector space
- Relationships are preserved (king - man + woman ≈ queen)
- This is done through neural networks with millions of parameters

**Q: Why 384 dimensions specifically?**
A: Model architecture choice balancing:
- Quality: More dimensions = more capacity to capture nuances
- Speed: Fewer dimensions = faster computation
- Memory: Fewer dimensions = less storage
- 384 is sweet spot for many models (BERT variants often use 768/1024)

**Q: Can I use different embedding models for query vs documents?**
A: **No!** Query and documents must use the **same** embedding model. Different models create incompatible vector spaces. You can't compare distances meaningfully across different spaces.

**Q: How do I handle multiple languages?**
A: Options:
1. **Multilingual models**: `paraphrase-multilingual-mpnet-base-v2` (supports 50+ languages)
2. **Separate indices per language**: Better quality but more complex
3. **Translation layer**: Translate everything to English first (adds latency)

**Q: What's the difference between embeddings and feature vectors?**
A:
- **Embeddings**: Learned representations (from neural networks)
- **Feature vectors**: Hand-crafted representations (TF-IDF, bag-of-words)
- Embeddings are generally much better at capturing semantic meaning

---

### Redis-Specific Questions

**Q: How much memory does Redis need for vectors?**
A: Calculate as:
```
Memory = num_vectors × dimensions × bytes_per_dimension × overhead_factor

Example for 1M vectors:
1,000,000 × 384 × 4 bytes × 1.3 (overhead) = ~2 GB

Overhead includes:
- Index structures (15-30% depending on algorithm)
- Redis memory allocation overhead
- Metadata storage
```

**Q: Can Redis handle billions of vectors?**
A: Yes, with clustering:
- Single node: Up to 100M vectors (depending on RAM)
- Redis Enterprise cluster: Billions of vectors (distributed)
- Use Redis Enterprise for production scale

**Q: What happens when Redis runs out of memory?**
A: Depends on `maxmemory-policy`:
```python
# View current policy
client.config_get('maxmemory-policy')

# Common policies:
# 'noeviction' - Return errors when full (safest for vector DB)
# 'allkeys-lru' - Evict least recently used (dangerous for vectors!)
# 'volatile-lru' - Evict only keys with TTL

# Recommended for vector DB:
client.config_set('maxmemory-policy', 'noeviction')
```

**Q: How does Redis compare to dedicated vector databases (Pinecone, Weaviate, Milvus)?**
A: 
**Redis Advantages:**
- Already in your stack (cache + vector DB)
- Sub-millisecond latency
- Mature, battle-tested
- Rich data structures beyond vectors

**Dedicated Vector DB Advantages:**
- More advanced features (filtering, faceting)
- Built specifically for vectors
- Better tooling for ML workflows

**Use Redis when:** You need low latency, already use Redis, want unified cache+vector
**Use dedicated DB when:** Pure vector workload, need advanced features

---

### Performance Questions

**Q: Why is my query slow?**
A: Debug checklist:
```python
# 1. Check algorithm
info = index.info()
print(info['vector_algorithm'])  # FLAT is slower than HNSW

# 2. Check dataset size
print(f"Documents: {info['num_docs']}")
# If >100K with FLAT, switch to HNSW

# 3. Profile query time
import time
start = time.time()
results = index.query(query)
print(f"Query time: {(time.time()-start)*1000:.2f}ms")

# 4. Check network latency
start = time.time()
client.ping()
print(f"Ping: {(time.time()-start)*1000:.2f}ms")

# 5. Check embedding time
start = time.time()
vec = hf.embed(text)
print(f"Embedding time: {(time.time()-start)*1000:.2f}ms")
```

**Q: When should I use HNSW vs FLAT?**
A:
```
FLAT (Exact Search):
✓ <100K vectors
✓ Need 100% accuracy
✓ Simple, no tuning
✗ O(N) complexity - slow on large datasets

HNSW (Approximate Search):
✓ >100K vectors
✓ Can tolerate 95-99% accuracy
✓ Much faster (10-100x)
✗ Uses more memory
✗ Requires parameter tuning

Rule of thumb:
- Start with FLAT
- Migrate to HNSW when queries slow down
- Test to find acceptable accuracy/speed tradeoff
```

**Q: How do I tune HNSW parameters?**
A:
```python
# Start with these defaults
attrs = {
    "algorithm": "hnsw",
    "m": 16,              # 16-64 range
    "ef_construction": 200,  # 100-500 range
    "ef_runtime": 10      # 10-200 range (set at query time)
}

# Tuning guide:
# m: Higher = better accuracy, more memory
#    Double m → 2x memory but ~10% better recall
    
# ef_construction: Higher = better index quality
#    Only affects indexing time (one-time cost)
#    Set as high as tolerable during indexing
    
# ef_runtime: Higher = better accuracy, slower queries
#    Adjust based on accuracy requirements
#    Tune via A/B testing

# Example tuning:
for ef in [10, 20, 50, 100]:
    query = VectorQuery(vector=v, ef_runtime=ef)
    results = index.query(query)
    # Measure accuracy vs speed
```

---

### Data Management Questions

**Q: How do I update vectors?**
A:
```python
# Option 1: Update entire document (recommended)
key = "movies:01K7T4BMAEZMNPYTV73KZFYN3R"
new_data = {
    "title": "Updated Title",
    "description": "New description",
    "vector": new_embedding
}
client.hset(key, mapping=new_data)
# Index updates automatically

# Option 2: Update just the vector
client.hset(key, "vector", new_embedding_bytes)

# Option 3: Bulk update
for key, new_embedding in updates.items():
    client.hset(key, "vector", new_embedding)
```

**Q: Can I have multiple vector fields per document?**
A: Yes! Useful for multi-modal search:
```python
schema = {
    "fields": [
        {
            "name": "title_vector",
            "type": "vector",
            "attrs": {"dims": 384, ...}
        },
        {
            "name": "description_vector",
            "type": "vector",
            "attrs": {"dims": 384, ...}
        },
        {
            "name": "image_vector",
            "type": "vector",
            "attrs": {"dims": 512, ...}  # Different model OK
        }
    ]
}

# Query specific field
query = VectorQuery(
    vector=query_vec,
    vector_field_name="title_vector"  # Search titles only
)
```

**Q: How do I handle document updates/deletes?**
A:
```python
# Delete document
client.delete("movies:01K7T4BMAEZMNPYTV73KZFYN3R")
# Index updates automatically

# Bulk delete
keys_to_delete = client.keys("movies:*")
if keys_to_delete:
    client.delete(*keys_to_delete)

# Conditional delete
for key in client.scan_iter("movies:*"):
    data = client.hgetall(key)
    if should_delete(data):
        client.delete(key)
```

---

### Search Quality Questions

**Q: How do I improve search quality?**
A: Multiple strategies:

**1. Better embeddings:**
```python
# Use larger, better models
# all-MiniLM-L6-v2 (384d) → all-mpnet-base-v2 (768d)
# or fine-tune on your domain data
```

**2. Hybrid search:**
```python
# Combine vector + text search (best approach)
HybridQuery(alpha=0.7)
```

**3. Query expansion:**
```python
# Add synonyms/related terms
original_query = "car"
expanded_query = "car automobile vehicle"
```

**4. Reranking:**
```python
# Two-stage retrieval
# Stage 1: Get 100 candidates (fast, approximate)
candidates = index.query(VectorQuery(num_results=100))

# Stage 2: Rerank top candidates (slow, accurate)
reranked = rerank_model.predict(query, candidates)
final_results = reranked[:10]
```

**5. Filter tuning:**
```python
# Pre-filter to high-quality subset
filter = (Num("rating") >= 4) & (Tag("verified") == "yes")
```

**Q: How do I evaluate search quality?**
A: Use standard IR metrics:
```python
# Precision@K: What % of top K results are relevant?
def precision_at_k(results, relevant_ids, k=10):
    top_k = [r['id'] for r in results[:k]]
    relevant_count = len(set(top_k) & set(relevant_ids))
    return relevant_count / k

# Recall@K: What % of relevant docs are in top K?
def recall_at_k(results, relevant_ids, k=10):
    top_k = [r['id'] for r in results[:k]]
    relevant_count = len(set(top_k) & set(relevant_ids))
    return relevant_count / len(relevant_ids)

# Mean Reciprocal Rank (MRR): Position of first relevant result
def mrr(results, relevant_ids):
    for i, result in enumerate(results, 1):
        if result['id'] in relevant_ids:
            return 1.0 / i
    return 0.0

# NDCG: Normalized Discounted Cumulative Gain
# (More complex, considers graded relevance)
```

---

### Production Considerations Questions

**Q: How do I handle high query volume?**
A:
```python
# 1. Use Redis Enterprise cluster (horizontal scaling)
# 2. Implement caching layer
# 3. Connection pooling
from redis import ConnectionPool

pool = ConnectionPool.from_url(REDIS_URL, max_connections=50)
client = Redis(connection_pool=pool)

# 4. Async queries (if using async framework)
from redisvl.index import AsyncSearchIndex

async_index = AsyncSearchIndex(schema, client)
results = await async_index.query(query)

# 5. Batch queries
queries = [query1, query2, query3]
results = await async_index.query_batch(queries)
```

**Q: How do I monitor Redis vector search?**
A:
```python
# Key metrics to track
info = index.info()

print(f"Documents: {info['num_docs']}")
print(f"Memory: {info['vector_index_sz_mb']} MB")
print(f"Indexing failures: {info['hash_indexing_failures']}")

# Query latency percentiles
# Use Redis monitoring tools or custom tracking:
import time
latencies = []

for query in test_queries:
    start = time.time()
    index.query(query)
    latencies.append((time.time() - start) * 1000)

import numpy as np
print(f"P50: {np.percentile(latencies, 50):.2f}ms")
print(f"P95: {np.percentile(latencies, 95):.2f}ms")
print(f"P99: {np.percentile(latencies, 99):.2f}ms")
```

**Q: Should I use Redis Cloud or self-hosted?**
A:
**Redis Cloud:**
✓ Managed, no ops burden
✓ Auto-scaling
✓ Built-in monitoring
✓ Multi-cloud support
✗ Cost (pay for managed service)

**Self-hosted:**
✓ Full control
✓ Lower cost (just infrastructure)
✗ Ops complexity
✗ Need monitoring/alerting setup

**Recommendation:** Start with Redis Cloud for development, decide based on scale/budget for production.

---

## Architecture & Performance

### System Architecture

**Typical Production Architecture:**
```
┌─────────────┐
│   Client    │
│ Application │
└──────┬──────┘
       │
       ↓
┌──────────────────┐
│  Load Balancer   │
└──────┬───────────┘
       │
       ↓
┌──────────────────┐     ┌────────────────┐
│   Application    │────→│  Embedding     │
│     Server       │     │    Service     │
│  (FastAPI/Flask) │     │ (Sentence-     │
└──────┬───────────┘     │  Transformers) │
       │                 └────────────────┘
       ↓
┌──────────────────┐
│   Redis Cloud    │
│  (with Search)   │
│                  │
│ ┌──────────────┐│
│ │ Vector Index ││
│ └──────────────┘│
│ ┌──────────────┐│
│ │ Cache Layer  ││
│ └──────────────┘│
└──────────────────┘
```

### Performance Benchmarks

**Query Latency (approximate):**
```
Dataset Size    Algorithm    Query Time
─────────────────────────────────────────
1K vectors      FLAT         1-2ms
10K vectors     FLAT         5-10ms
100K vectors    FLAT         50-100ms  ← Switch to HNSW here
100K vectors    HNSW         2-5ms
1M vectors      HNSW         3-8ms
10M vectors     HNSW         5-15ms
```

**Throughput (queries/second):**
```
Single Redis node: 5,000-10,000 QPS
Redis Enterprise (10 nodes): 50,000-100,000 QPS
```

### Memory Optimization

**Techniques to reduce memory:**
```python
# 1. Use smaller embeddings
# 384d instead of 1536d = 4x less memory

# 2. Quantization (reduce precision)
attrs = {
    "datatype": "float16"  # 2 bytes instead of 4
}
# Trades accuracy for 2x memory savings

# 3. SVS-VAMANA with compression
attrs = {
    "algorithm": "svs-vamana",
    "compression": "lvq8"  # 8-bit compression
}

# 4. Store vectors separately from metadata
# Use JSON for metadata, vectors in separate keys
```

---

## Production Considerations

### Best Practices

**1. Schema Design:**
```python
# ✓ Good: Specific prefixes
prefix = "product_vectors"  # Clear purpose

# ✗ Bad: Generic prefixes
prefix = "data"  # Too vague

# ✓ Good: Version schemas
prefix = "product_vectors_v2"  # Enables migrations

# ✓ Good: Document structure
{
    "id": "prod_123",
    "title": "...",
    "description": "...",
    "vector": b"...",
    "metadata": {
        "created_at": "2025-01-01",
        "updated_at": "2025-01-15"
    }
}
```

**2. Error Handling:**
```python
from redis.exceptions import RedisError, TimeoutError

try:
    results = index.query(query)
except TimeoutError:
    # Retry with exponential backoff
    logger.error("Redis timeout, retrying...")
    results = retry_with_backoff(index.query, query)
except RedisError as e:
    # Log and return cached/default results
    logger.error(f"Redis error: {e}")
    results = get_cached_results(query)
except Exception as e:
    # Catch-all
    logger.exception("Unexpected error")
    raise
```

**3. Caching Strategy:**
```python
# Multi-layer caching
class VectorSearchService:
    def __init__(self):
        self.local_cache = {}  # In-memory (milliseconds)
        self.redis_cache = redis_client  # Redis cache (1-2ms)
        self.index = search_index  # Vector search (5-10ms)
    
    def search(self, query):
        cache_key = hash(query)
        
        # L1: Check local memory
        if cache_key in self.local_cache:
            return self.local_cache[cache_key]
        
        # L2: Check Redis cache
        cached = self.redis_cache.get(f"search:{cache_key}")
        if cached:
            results = json.loads(cached)
            self.local_cache[cache_key] = results
            return results
        
        # L3: Perform search
        results = self.index.query(query)
        
        # Cache results
        self.redis_cache.setex(
            f"search:{cache_key}",
            3600,  # 1 hour TTL
            json.dumps(results)
        )
        self.local_cache[cache_key] = results
        
        return results
```

**4. Monitoring & Alerting:**
```python
# Metrics to track
metrics = {
    "query_latency_p50": ...,
    "query_latency_p95": ...,
    "query_latency_p99": ...,
    "queries_per_second": ...,
    "error_rate": ...,
    "cache_hit_rate": ...,
    "index_memory_mb": ...,
    "document_count": ...,
}

# Alerts
if metrics["query_latency_p99"] > 100:  # >100ms
    alert("High query latency!")

if metrics["error_rate"] > 0.01:  # >1%
    alert("High error rate!")

if metrics["index_memory_mb"] > 0.8 * max_memory:
    alert("Redis memory almost full!")
```

**5. Deployment Checklist:**
```
□ Enable SSL/TLS (rediss://)
□ Set strong password
□ Configure maxmemory-policy (noeviction for vector DB)
□ Set up monitoring (Prometheus, Datadog, etc.)
□ Configure backups (AOF or RDB)
□ Test failover scenarios
□ Load test at 2x expected traffic
□ Document schema and indices
□ Set up alerting
□ Plan capacity (memory, QPS)
```

---

## Conclusion & Key Takeaways

### Core Concepts Mastered
1. ✅ Vector embeddings capture semantic meaning
2. ✅ Redis provides sub-millisecond vector search
3. ✅ Multiple search types: Vector, Range, Text, Hybrid
4. ✅ Hybrid search combines best of semantic + keyword
5. ✅ Filters enable precise, constrained search
6. ✅ RedisVL simplifies vector operations in Python

### Decision Framework

**Choose your search approach:**
```
Pure Vector Search
├─ When: Understanding meaning matters most
├─ Example: "Find similar products"
└─ Use: VectorQuery

Pure Text Search
├─ When: Exact keywords critical
├─ Example: "Find document #12345"
└─ Use: TextQuery

Hybrid Search (Recommended!)
├─ When: Production applications (usually best)
├─ Example: Most real-world search scenarios
└─ Use: HybridQuery with alpha=0.7

Range Search
├─ When: Quality threshold matters
├─ Example: "Show all similar enough items"
└─ Use: RangeQuery
```

### Production Readiness
- Start simple (FLAT algorithm)
- Scale up (migrate to HNSW at 100K+ vectors)
- Monitor continuously (latency, memory, errors)
- Cache aggressively (embeddings, query results)
- Test thoroughly (accuracy, speed, scale)

### Next Steps for Attendees
1. Try with your own data
2. Experiment with different embedding models
3. Tune hybrid search alpha parameter
4. Deploy to Redis Cloud
5. Integrate with your application
6. Measure and optimize

---

## Additional Resources

- **RedisVL Documentation**: https://www.redisvl.com/
- **Redis Vector Search Guide**: https://redis.io/docs/stack/search/reference/vectors/
- **Sentence Transformers**: https://www.sbert.net/
- **Redis AI Resources**: https://github.com/redis-developer/redis-ai-resources
- **Redis University**: https://university.redis.com/

---

**Workshop Complete!** 🎉

You now have the knowledge to build production-grade semantic search applications with Redis and RedisVL.