# Investigation Guide - Redis Context Course Agent

This guide helps you diagnose and troubleshoot issues with the Redis Context Course agent system.

## Quick Diagnosis

### Primary Health Check
```bash
python simple_health_check.py
```

This is your **first stop** for any issues. It checks:
- ✅ Environment variables
- ✅ Redis connection
- ✅ Course and major data
- ✅ Search functionality
- ✅ Agent responses

### Comprehensive Diagnostics
```bash
python system_health_check.py --verbose
```

Use this for detailed analysis including:
- Performance metrics
- Data quality validation
- Detailed error messages
- Binary data handling

## Common Issues & Solutions

### 1. "Environment: Missing OPENAI_API_KEY"
**Problem**: OpenAI API key not set or using placeholder value

**Solution**:
```bash
# Edit .env file
nano .env

# Set your actual API key
OPENAI_API_KEY=sk-your-actual-key-here
```

### 2. "Redis: Connection failed"
**Problem**: Redis server not running

**Solution**:
```bash
# Start Redis with Docker
docker run -d --name redis -p 6379:6379 redis:8-alpine

# Or check if Redis is already running
docker ps | grep redis
```

### 3. "Courses: None found"
**Problem**: Course data not ingested

**Solution**:
```bash
# Generate sample data if needed
generate-courses --courses-per-major 15 --output course_catalog.json

# Ingest with embeddings
ingest-courses --catalog course_catalog.json --clear
```

### 4. "Course Search: Failed"
**Problem**: Search functionality not working

**Possible Causes**:
- Courses ingested without embeddings
- OpenAI API key issues during ingestion
- Vector index corruption

**Solution**:
```bash
# Re-ingest with fresh embeddings
ingest-courses --catalog course_catalog.json --clear

# Verify API key works
python -c "from openai import OpenAI; print(OpenAI().models.list())"
```

### 5. "Agent: Failed"
**Problem**: Agent cannot respond to queries

**Possible Causes**:
- Tool configuration issues
- Memory server not running
- Course search not working

**Solution**:
```bash
# Check Agent Memory Server
curl http://localhost:8088/health

# Start if needed
uv run agent-memory api --no-worker

# Test individual components
python -c "
import asyncio
from redis_context_course import ClassAgent
async def test():
    agent = ClassAgent('test')
    print(await agent.chat('Hello'))
asyncio.run(test())
"
```

## Investigation Workflow

### Step 1: Quick Check
```bash
python simple_health_check.py
```

### Step 2: If Issues Found
1. **Follow the fix commands** provided in the output
2. **Re-run the health check** to verify fixes
3. **Check logs** for detailed error messages

### Step 3: Deep Dive (if needed)
```bash
python system_health_check.py --verbose
```

### Step 4: Component Testing
Test individual components if the agent still fails:

```bash
# Test Redis directly
redis-cli ping

# Test course manager
python -c "
import asyncio
from redis_context_course.course_manager import CourseManager
async def test():
    cm = CourseManager()
    courses = await cm.search_courses('programming')
    print(f'Found {len(courses)} courses')
asyncio.run(test())
"

# Test OpenAI connection
python -c "
from openai import OpenAI
client = OpenAI()
response = client.embeddings.create(
    model='text-embedding-ada-002',
    input='test'
)
print('OpenAI connection working')
"
```

## Data Validation

### Check Redis Data Patterns
```bash
# Connect to Redis
redis-cli

# Check data patterns
KEYS major:*
KEYS course_catalog:*
KEYS *memory*

# Sample a course record
HGETALL course_catalog:01K897CBGQYD2EPGNYKNYKJ88J
```

### Verify Vector Embeddings
Vector embeddings are stored as binary data - this is normal:
- ✅ `content_vector` field contains binary data
- ✅ Cannot be read as text (this is expected)
- ✅ Used by Redis for semantic search

## Performance Issues

### Slow Responses
```bash
# Check with performance metrics
python system_health_check.py --verbose

# Look for:
# - High response times (>2000ms)
# - Redis memory usage
# - OpenAI API latency
```

### Memory Usage
```bash
# Check Redis memory
redis-cli INFO memory

# Check course count vs memory
redis-cli DBSIZE
```

## Deprecated Scripts

These scripts are **deprecated** - use the health checks instead:
- ❌ `simple_check.py` - Only checks Redis keys
- ❌ `test_agent.py` - Basic functionality test
- ❌ `debug_agent.py` - Tool debugging
- ❌ `verify_courses.py` - Course verification
- ❌ `final_test.py` - Comprehensive test

## Getting Help

### Log Analysis
Check for error patterns in the health check output:
- `UnicodeDecodeError` - Normal for binary vector data
- `ConnectionError` - Redis/network issues
- `AuthenticationError` - OpenAI API key issues
- `ImportError` - Package installation issues

### Environment Debug
```bash
# Check environment
env | grep -E "(REDIS|OPENAI|AGENT)"

# Check package installation
pip list | grep redis-context-course

# Check Python path
python -c "import redis_context_course; print(redis_context_course.__file__)"
```

### Reset Everything
If all else fails, complete reset:
```bash
# Stop containers
docker stop redis agent-memory

# Remove containers
docker rm redis agent-memory

# Clear Redis data
docker run --rm -v redis_data:/data redis:8-alpine rm -rf /data/*

# Start fresh
docker run -d --name redis -p 6379:6379 redis:8-alpine
uv run agent-memory api --no-worker

# Re-ingest data
ingest-courses --catalog course_catalog.json --clear

# Test
python simple_health_check.py
```

## Success Indicators

When everything is working correctly:
```
✅ Environment: All variables set
✅ Redis: Connected
✅ Courses: 75 found
✅ Majors: 5 found
✅ Course Search: Working
✅ Agent: Working

🎯 Status: READY
📊 All checks passed!
```

You can then use the agent:
```bash
redis-class-agent --student-id your_name
```
