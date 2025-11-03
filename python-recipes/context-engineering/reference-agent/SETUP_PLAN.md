# Setup Plan - Redis Context Course Agent

Complete step-by-step plan for setting up and testing the Redis Context Course agent.

## Prerequisites

- Python 3.8+
- Docker (for Redis and Agent Memory Server)
- OpenAI API key
- Terminal/command line access

## Phase 1: Environment Setup

### 1.1 Install Package
```bash
# From source (recommended for development)
cd python-recipes/context-engineering/reference-agent
pip install -e .

# Or from PyPI
pip install redis-context-course
```

### 1.2 Configure Environment
```bash
# Copy example environment file
cp .env.example .env

# Edit with your settings
nano .env
```

Required variables:
```bash
OPENAI_API_KEY=sk-your-actual-openai-key
REDIS_URL=redis://localhost:6379
AGENT_MEMORY_URL=http://localhost:8088
```

### 1.3 Verify Installation
```bash
# Check package installation
pip list | grep redis-context-course

# Check command availability
which redis-class-agent
which generate-courses
which ingest-courses
```

## Phase 2: Infrastructure Setup

### 2.1 Start Redis
```bash
# Using Docker (recommended)
docker run -d --name redis -p 6379:6379 redis:8-alpine

# Verify Redis is running
docker ps | grep redis
redis-cli ping  # Should return PONG
```

### 2.2 Start Agent Memory Server
```bash
# Install if needed
pip install agent-memory-server

# Start server (in separate terminal)
uv run agent-memory api --no-worker

# Or with Docker
docker run -d --name agent-memory \
  -p 8088:8000 \
  -e REDIS_URL=redis://host.docker.internal:6379 \
  -e OPENAI_API_KEY=your-key \
  redis/agent-memory-server

# Verify server is running
curl http://localhost:8088/health
```

### 2.3 Initial Health Check
```bash
python simple_health_check.py
```

Expected at this stage:
- ✅ Environment: All variables set
- ✅ Redis: Connected
- ❌ Courses: None found (expected)
- ❌ Majors: None found (expected)

## Phase 3: Data Setup

### 3.1 Generate Sample Data
```bash
generate-courses --courses-per-major 15 --output course_catalog.json
```

This creates:
- 75 courses across 5 majors
- Realistic course data with descriptions
- JSON format ready for ingestion

### 3.2 Ingest Data into Redis
```bash
ingest-courses --catalog course_catalog.json --clear
```

This process:
- Clears existing data
- Ingests majors and courses
- Generates vector embeddings via OpenAI
- Creates searchable indexes

**Expected output:**
```
✅ Cleared existing data
✅ Ingested 5 majors
✅ Ingested 75 courses with embeddings
✅ Created vector indexes
```

### 3.3 Verify Data Ingestion
```bash
python simple_health_check.py
```

Expected after ingestion:
- ✅ Environment: All variables set
- ✅ Redis: Connected
- ✅ Courses: 75 found
- ✅ Majors: 5 found
- ✅ Course Search: Working
- ✅ Agent: Working

## Phase 4: Functionality Testing

### 4.1 Test Course Search
```bash
python -c "
import asyncio
from redis_context_course.course_manager import CourseManager

async def test():
    cm = CourseManager()
    courses = await cm.search_courses('programming', limit=3)
    for course in courses:
        print(f'{course.course_code}: {course.title}')

asyncio.run(test())
"
```

### 4.2 Test Agent Functionality
```bash
python -c "
import asyncio
from redis_context_course import ClassAgent

async def test():
    agent = ClassAgent('test_student')
    response = await agent.chat('How many courses are available?')
    print(response)

asyncio.run(test())
"
```

### 4.3 Test CLI Interface
```bash
# Start interactive agent
redis-class-agent --student-id test_user

# Try these queries:
# - "How many courses are there?"
# - "Show me programming courses"
# - "I'm interested in machine learning"
# - "What courses should I take for computer science?"
```

## Phase 5: Validation & Troubleshooting

### 5.1 Comprehensive Health Check
```bash
python system_health_check.py --verbose
```

This provides:
- Performance metrics
- Data quality validation
- Detailed diagnostics
- Binary data handling verification

### 5.2 Common Issues Resolution

**Issue: Course ingestion fails**
```bash
# Check OpenAI API key
python -c "from openai import OpenAI; print(OpenAI().models.list())"

# Re-run with fresh data
ingest-courses --catalog course_catalog.json --clear
```

**Issue: Agent doesn't respond**
```bash
# Check Agent Memory Server
curl http://localhost:8088/health

# Restart if needed
pkill -f "agent-memory"
uv run agent-memory api --no-worker
```

**Issue: Search returns no results**
```bash
# Check if embeddings were created
redis-cli HGET course_catalog:01K897CBGQYD2EPGNYKNYKJ88J content_vector

# Should return binary data (not readable text)
```

### 5.3 Performance Validation
Expected performance benchmarks:
- Course search: <500ms
- Agent response: <3000ms
- Redis operations: <50ms
- Memory usage: <100MB for 75 courses

## Phase 6: Production Readiness

### 6.1 Security Checklist
- [ ] OpenAI API key secured (not in version control)
- [ ] Redis access restricted (if networked)
- [ ] Agent Memory Server secured
- [ ] Environment variables properly set

### 6.2 Monitoring Setup
```bash
# Redis monitoring
redis-cli INFO stats

# Memory usage
redis-cli INFO memory

# Agent Memory Server health
curl http://localhost:8088/health
```

### 6.3 Backup Strategy
```bash
# Backup Redis data
redis-cli BGSAVE

# Backup course catalog
cp course_catalog.json course_catalog_backup.json

# Backup environment
cp .env .env.backup
```

## Success Criteria

### Functional Requirements
- ✅ Agent responds to course queries
- ✅ Search finds relevant courses
- ✅ Memory system stores preferences
- ✅ Recommendations work correctly
- ✅ CLI interface is responsive

### Performance Requirements
- ✅ Course search <500ms
- ✅ Agent responses <3000ms
- ✅ System handles 75+ courses
- ✅ Memory usage reasonable

### Quality Requirements
- ✅ All health checks pass
- ✅ No critical errors in logs
- ✅ Consistent behavior across sessions
- ✅ Proper error handling

## Maintenance Plan

### Daily
- Monitor health check status
- Check system performance
- Verify agent responsiveness

### Weekly
- Review memory usage trends
- Check for API rate limits
- Validate data integrity

### Monthly
- Update dependencies
- Review and optimize performance
- Backup critical data

## Rollback Plan

If issues occur:

1. **Stop services**:
   ```bash
   docker stop redis agent-memory
   ```

2. **Restore from backup**:
   ```bash
   cp .env.backup .env
   cp course_catalog_backup.json course_catalog.json
   ```

3. **Restart with clean state**:
   ```bash
   docker start redis
   uv run agent-memory api --no-worker
   ingest-courses --catalog course_catalog.json --clear
   ```

4. **Verify restoration**:
   ```bash
   python simple_health_check.py
   ```

## Next Steps

After successful setup:

1. **Explore examples**: Check `examples/` directory
2. **Read documentation**: Review README.md thoroughly
3. **Customize agent**: Modify tools and behavior
4. **Integrate**: Connect to your applications
5. **Scale**: Consider production deployment

## Support Resources

- **Health Check**: `python simple_health_check.py`
- **Investigation Guide**: `INVESTIGATION_GUIDE.md`
- **Examples**: `examples/basic_usage.py`
- **Tests**: `pytest tests/`
- **Documentation**: `README.md`
