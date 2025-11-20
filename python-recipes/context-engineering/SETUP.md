# Setup Guide for Context Engineering Course

This guide will help you set up everything you need to run the Context Engineering notebooks and reference agent.

## Prerequisites

- **Python 3.10+** installed
- **Docker and Docker Compose** installed
- **OpenAI API key** (get one at https://platform.openai.com/api-keys)

## Quick Setup (5 minutes)

### Step 1: Set Your OpenAI API Key

The OpenAI API key is needed by both the Jupyter notebooks AND the Agent Memory Server. The easiest way to set it up is to use a `.env` file.

```bash
# Navigate to the context-engineering directory
cd python-recipes/context-engineering

# Copy the example environment file
cp .env.example .env

# Edit .env and add your OpenAI API key
# Replace 'your-openai-api-key-here' with your actual key
```

Your `.env` file should look like this:
```bash
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxx
REDIS_URL=redis://localhost:6379
AGENT_MEMORY_URL=http://localhost:8088
```

**Important:** The `.env` file is already in `.gitignore` so your API key won't be committed to git.

### Step 2: Start Required Services

Start Redis and the Agent Memory Server using Docker Compose:

```bash
# Start services in the background
docker-compose up -d

# Verify services are running
docker-compose ps

# Check that the Agent Memory Server is healthy
curl http://localhost:8088/v1/health
```

You should see:
- `redis-context-engineering` running on port 6379 (Redis 8)
- `agent-memory-server` running on port 8088

### Step 3: Install Python Dependencies

```bash
# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install notebook dependencies (Jupyter, python-dotenv, etc.)
pip install -r requirements.txt

# Install the reference agent package
cd reference-agent
pip install -e .
cd ..
```

### Step 4: Run the Notebooks

```bash
# Start Jupyter from the context-engineering directory
jupyter notebook notebooks/

# Open any notebook and run the cells
```

The notebooks will automatically load your `.env` file using `python-dotenv`, so your `OPENAI_API_KEY` will be available.

## Verifying Your Setup

### Check Redis
```bash
# Test Redis connection
docker exec redis-context-engineering redis-cli ping
# Should return: PONG
```

### Check Agent Memory Server
```bash
# Test health endpoint
curl http://localhost:8088/v1/health
# Should return: {"now":<timestamp>}

# Test that it can connect to Redis and has your API key
curl http://localhost:8088/api/v1/namespaces
# Should return a list of namespaces (may be empty initially)
```

### Check Python Environment
```bash
# Verify the reference agent package is installed
python -c "import redis_context_course; print('✅ Package installed')"

# Verify OpenAI key is set
python -c "import os; print('✅ OpenAI key set' if os.getenv('OPENAI_API_KEY') else '❌ OpenAI key not set')"
```

## Troubleshooting

### "OPENAI_API_KEY not found"

**In Notebooks:** The notebooks will prompt you for your API key if it's not set. However, it's better to set it in the `.env` file so you don't have to enter it repeatedly.

**In Docker:** Make sure:
1. Your `.env` file exists and contains `OPENAI_API_KEY=your-key`
2. You've restarted the services: `docker-compose down && docker-compose up -d`
3. Check the logs: `docker-compose logs agent-memory-server`

### "Connection refused" to Agent Memory Server

Make sure the services are running:
```bash
docker-compose ps
```

If they're not running, start them:
```bash
docker-compose up -d
```

Check the logs for errors:
```bash
docker-compose logs agent-memory-server
```

### "Connection refused" to Redis

Make sure Redis is running:
```bash
docker-compose ps redis
```

Test the connection:
```bash
docker exec redis-context-engineering redis-cli ping
```

### Port Already in Use

If you get errors about ports already in use (6379 or 8088), you can either:

1. Stop the conflicting service
2. Change the ports in `docker-compose.yml`:
   ```yaml
   ports:
     - "6380:6379"  # Use 6380 instead of 6379
   ```
   Then update `REDIS_URL` or `AGENT_MEMORY_URL` in your `.env` file accordingly.

## Stopping Services

```bash
# Stop services but keep data
docker-compose stop

# Stop and remove services (keeps volumes/data)
docker-compose down

# Stop and remove everything including data
docker-compose down -v
```

## Alternative: Using Existing Redis or Cloud Redis

If you already have Redis running or want to use Redis Cloud:

1. Update `REDIS_URL` in your `.env` file:
   ```bash
   REDIS_URL=redis://default:password@your-redis-cloud-url:port
   ```

2. You still need to run the Agent Memory Server locally:
   ```bash
   docker-compose up -d agent-memory-server
   ```

## Next Steps

Once setup is complete:

1. Start with **Section 1** notebooks to understand core concepts
2. Work through **Section 2** to learn system context setup
3. Complete **Section 3** to master memory management (requires Agent Memory Server)
4. Explore **Section 4** for advanced optimization techniques

## Getting Help

- Check the main [README.md](README.md) for course structure and learning path
- Review [COURSE_SUMMARY.md](COURSE_SUMMARY.md) for an overview of all topics
- Open an issue if you encounter problems with the setup

