# 🚀 Setup Guide for Context Engineering Notebooks

This guide helps you set up all required services for the Context Engineering course notebooks.

## 📋 Prerequisites

Before running any notebooks, you need:

1. **Docker Desktop** - For Redis and Agent Memory Server
2. **Python 3.8+** - For running notebooks
3. **OpenAI API Key** - For LLM functionality

## ⚡ Quick Setup (Recommended)

### Option 1: Automated Setup Script (Bash)

```bash
# Navigate to notebooks directory
cd python-recipes/context-engineering/notebooks_v2

# Run the setup script
./setup_memory_server.sh
```

This script will:
- ✅ Check Docker is running
- ✅ Start Redis if needed
- ✅ Start Agent Memory Server
- ✅ Verify all connections work

### Option 2: Python Setup Script

```bash
# Navigate to notebooks directory
cd python-recipes/context-engineering/notebooks_v2

# Run Python setup
python setup_memory_server.py
```

## 🔧 Manual Setup

If you prefer to set up services manually:

### 1. Environment Variables

Create a `.env` file in the `reference-agent/` directory:

```bash
# Navigate to reference-agent directory
cd python-recipes/context-engineering/reference-agent

# Create .env file
cat > .env << EOF
OPENAI_API_KEY=your_openai_api_key_here
REDIS_URL=redis://localhost:6379
AGENT_MEMORY_URL=http://localhost:8088
OPENAI_MODEL=gpt-4o
EOF
```

### 2. Start Redis

```bash
docker run -d --name redis-stack-server -p 6379:6379 redis/redis-stack-server:latest
```

### 3. Start Agent Memory Server

```bash
docker run -d --name agent-memory-server \
    -p 8088:8000 \
    -e REDIS_URL=redis://host.docker.internal:6379 \
    -e OPENAI_API_KEY="your_openai_api_key_here" \
    ghcr.io/redis/agent-memory-server:0.12.3
```

## ✅ Verify Setup

### Quick Check (Recommended)

```bash
# Navigate to notebooks_v2 directory
cd python-recipes/context-engineering/notebooks_v2

# Run setup checker
./check_setup.sh
```

This will check all services and show you exactly what's working and what needs attention.

### Manual Verification

If you prefer to check manually:

```bash
# Check Redis
redis-cli ping
# Should return: PONG

# Check Agent Memory Server
curl http://localhost:8088/v1/health
# Should return: {"status":"ok"}

# Check Docker containers
docker ps
# Should show both redis-stack-server and agent-memory-server
```

## 🚨 Troubleshooting

### Redis Connection Issues

If you see Redis connection errors:

```bash
# Stop and restart Agent Memory Server
docker stop agent-memory-server
docker rm agent-memory-server

# Restart with correct Redis URL
docker run -d --name agent-memory-server \
    -p 8088:8000 \
    -e REDIS_URL=redis://host.docker.internal:6379 \
    -e OPENAI_API_KEY="your_openai_api_key_here" \
    ghcr.io/redis/agent-memory-server:0.12.3
```

### Port Conflicts

If ports 6379 or 8088 are in use:

```bash
# Check what's using the ports
lsof -i :6379
lsof -i :8088

# Stop conflicting services or use different ports
```

### Docker Issues

If Docker commands fail:

1. Make sure Docker Desktop is running
2. Check Docker has enough resources allocated
3. Try restarting Docker Desktop

## 📚 Next Steps

Once setup is complete:

1. **Start with Section 1** if you're new to context engineering
2. **Jump to Section 4** if you want to learn about memory tools and agents
3. **Check the README** in each section for specific requirements

## 🔗 Section-Specific Requirements

### Section 3 & 4: Memory Systems & Tools/Agents
- ✅ Redis (for vector storage)
- ✅ Agent Memory Server (for memory management)
- ✅ OpenAI API key

### Section 2: RAG Foundations  
- ✅ Redis (for vector storage)
- ✅ OpenAI API key

### Section 1: Context Foundations
- ✅ OpenAI API key only

---

**Need help?** Check the troubleshooting section or review the setup scripts for detailed error handling.
