# Agent Memory Server Setup Guide

This guide explains how to set up and run the Agent Memory Server for the context engineering notebooks.

## Quick Start

### Automated Setup (Recommended)

Run the setup script to automatically configure and start all required services:

```bash
# From the reference-agent directory
python setup_agent_memory_server.py
```

Or use the bash version:

```bash
# From the reference-agent directory
./setup_agent_memory_server.sh
```

The script will:
- ✅ Check if Docker is running
- ✅ Start Redis if not running (port 6379)
- ✅ Start Agent Memory Server if not running (port 8088)
- ✅ Verify Redis connection is working
- ✅ Handle any configuration issues automatically

### Expected Output

```
🔧 Agent Memory Server Setup
===========================
📊 Checking Redis...
✅ Redis is running
📊 Checking Agent Memory Server...
🚀 Starting Agent Memory Server...
⏳ Waiting for server to be ready...
✅ Agent Memory Server is ready!
🔍 Verifying Redis connection...

✅ Setup Complete!
=================
📊 Services Status:
   • Redis: Running on port 6379
   • Agent Memory Server: Running on port 8088

🎯 You can now run the notebooks!
```

## Prerequisites

1. **Docker Desktop** - Must be installed and running
2. **Environment Variables** - Create a `.env` file in this directory with:
   ```
   OPENAI_API_KEY=your_openai_api_key
   REDIS_URL=redis://localhost:6379
   AGENT_MEMORY_URL=http://localhost:8088
   ```

## Manual Setup

If you prefer to set up services manually:

### 1. Start Redis

```bash
docker run -d --name redis-stack-server -p 6379:6379 redis/redis-stack-server:latest
```

### 2. Start Agent Memory Server

```bash
docker run -d --name agent-memory-server \
  -p 8088:8000 \
  -e REDIS_URL=redis://host.docker.internal:6379 \
  -e OPENAI_API_KEY=your_openai_api_key \
  ghcr.io/redis/agent-memory-server:0.12.3
```

### 3. Verify Setup

```bash
# Check Redis
docker ps --filter name=redis-stack-server

# Check Agent Memory Server
docker ps --filter name=agent-memory-server

# Test health endpoint
curl http://localhost:8088/v1/health
```

## Troubleshooting

### Docker Not Running

**Error:** `Docker is not running`

**Solution:** Start Docker Desktop and wait for it to fully start, then run the setup script again.

### Redis Connection Error

**Error:** `ConnectionError: Error -2 connecting to redis:6379`

**Solution:** This means the Agent Memory Server can't connect to Redis. The setup script will automatically fix this by restarting the container with the correct configuration.

### Port Already in Use

**Error:** `port is already allocated`

**Solution:** 
```bash
# Find what's using the port
lsof -i :8088  # or :6379 for Redis

# Stop the conflicting container
docker stop <container_name>
```

### Agent Memory Server Not Responding

**Error:** `Timeout waiting for Agent Memory Server`

**Solution:**
```bash
# Check the logs
docker logs agent-memory-server

# Restart the container
docker stop agent-memory-server
docker rm agent-memory-server
python setup_agent_memory_server.py
```

### Missing OPENAI_API_KEY

**Error:** `OPENAI_API_KEY not set`

**Solution:** Create or update your `.env` file:
```bash
echo "OPENAI_API_KEY=sk-your-actual-key-here" > .env
```

## Checking Service Status

### View Running Containers

```bash
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

### Check Logs

```bash
# Redis logs
docker logs redis-stack-server

# Agent Memory Server logs
docker logs agent-memory-server
```

### Test Connections

```bash
# Test Redis
redis-cli ping
# Should return: PONG

# Test Agent Memory Server
curl http://localhost:8088/v1/health
# Should return: {"status":"ok"}
```

## Stopping Services

### Stop All Services

```bash
docker stop redis-stack-server agent-memory-server
```

### Remove Containers

```bash
docker rm redis-stack-server agent-memory-server
```

### Clean Restart

```bash
# Stop and remove everything
docker stop redis-stack-server agent-memory-server
docker rm redis-stack-server agent-memory-server

# Run setup script to start fresh
python setup_agent_memory_server.py
```

## Integration with Notebooks

The Section 3 notebooks automatically run the setup check when you execute them. You'll see output like:

```
Running automated setup check...

🔧 Agent Memory Server Setup
===========================
✅ All services are ready!
```

If the setup check fails, follow the error messages to resolve the issue before continuing with the notebook.

## Advanced Configuration

### Custom Redis URL

If you're using a different Redis instance:

```bash
# Update .env file
REDIS_URL=redis://your-redis-host:6379

# Or pass directly to Docker
docker run -d --name agent-memory-server \
  -p 8088:8000 \
  -e REDIS_URL=redis://your-redis-host:6379 \
  -e OPENAI_API_KEY=your_openai_api_key \
  ghcr.io/redis/agent-memory-server:0.12.3
```

### Different Port

To use a different port for Agent Memory Server:

```bash
# Map to different external port (e.g., 9000)
docker run -d --name agent-memory-server \
  -p 9000:8000 \
  -e REDIS_URL=redis://host.docker.internal:6379 \
  -e OPENAI_API_KEY=your_openai_api_key \
  ghcr.io/redis/agent-memory-server:0.12.3

# Update .env file
AGENT_MEMORY_URL=http://localhost:9000
```

## Docker Compose (Alternative)

For a more integrated setup, you can use docker-compose:

```yaml
version: '3.8'
services:
  redis:
    image: redis/redis-stack-server:latest
    ports:
      - "6379:6379"
  
  agent-memory:
    image: ghcr.io/redis/agent-memory-server:0.12.3
    ports:
      - "8088:8000"
    environment:
      - REDIS_URL=redis://redis:6379
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    depends_on:
      - redis
```

Then run:
```bash
docker-compose up -d
```

## Support

If you encounter issues not covered here:

1. Check the [Agent Memory Server documentation](https://github.com/redis/agent-memory-server)
2. Review the Docker logs for detailed error messages
3. Ensure your `.env` file is properly configured
4. Verify Docker Desktop has sufficient resources allocated

