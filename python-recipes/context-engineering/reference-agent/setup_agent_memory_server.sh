#!/bin/bash
# Setup script for Agent Memory Server
# This script ensures the Agent Memory Server is running with correct configuration

set -e  # Exit on error

echo "🔧 Agent Memory Server Setup"
echo "=============================="

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Check if OPENAI_API_KEY is set
if [ -z "$OPENAI_API_KEY" ]; then
    echo "❌ Error: OPENAI_API_KEY not set"
    echo "   Please set it in your .env file or environment"
    exit 1
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running"
    echo "   Please start Docker Desktop and try again"
    exit 1
fi

# Check if Redis is running
echo "📊 Checking Redis..."
if ! docker ps --filter name=redis-stack-server --format '{{.Names}}' | grep -q redis-stack-server; then
    echo "⚠️  Redis not running. Starting Redis..."
    docker run -d --name redis-stack-server -p 6379:6379 redis/redis-stack-server:latest
    echo "✅ Redis started"
else
    echo "✅ Redis is running"
fi

# Check if Agent Memory Server is running
echo "📊 Checking Agent Memory Server..."
if docker ps --filter name=agent-memory-server --format '{{.Names}}' | grep -q agent-memory-server; then
    echo "🔍 Agent Memory Server container exists. Checking health..."
    
    # Check if it's healthy by testing the connection
    if curl -s http://localhost:8088/v1/health > /dev/null 2>&1; then
        echo "✅ Agent Memory Server is running and healthy"
        
        # Check logs for Redis connection errors
        if docker logs agent-memory-server --tail 50 2>&1 | grep -q "ConnectionError.*redis"; then
            echo "⚠️  Detected Redis connection issues. Restarting with correct configuration..."
            docker stop agent-memory-server > /dev/null 2>&1
            docker rm agent-memory-server > /dev/null 2>&1
        else
            echo "✅ No Redis connection issues detected"
            exit 0
        fi
    else
        echo "⚠️  Agent Memory Server not responding. Restarting..."
        docker stop agent-memory-server > /dev/null 2>&1
        docker rm agent-memory-server > /dev/null 2>&1
    fi
fi

# Start Agent Memory Server with correct configuration
echo "🚀 Starting Agent Memory Server..."
docker run -d --name agent-memory-server \
    -p 8088:8000 \
    -e REDIS_URL=redis://host.docker.internal:6379 \
    -e OPENAI_API_KEY="$OPENAI_API_KEY" \
    ghcr.io/redis/agent-memory-server:0.12.3

# Wait for server to be healthy
echo "⏳ Waiting for server to be ready..."
for i in {1..30}; do
    if curl -s http://localhost:8088/v1/health > /dev/null 2>&1; then
        echo "✅ Agent Memory Server is ready!"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "❌ Timeout waiting for Agent Memory Server"
        echo "   Check logs with: docker logs agent-memory-server"
        exit 1
    fi
    sleep 1
done

# Verify no Redis connection errors
echo "🔍 Verifying Redis connection..."
sleep 2
if docker logs agent-memory-server --tail 20 2>&1 | grep -q "ConnectionError.*redis"; then
    echo "❌ Redis connection error detected"
    echo "   Logs:"
    docker logs agent-memory-server --tail 20
    exit 1
fi

echo ""
echo "✅ Setup Complete!"
echo "=============================="
echo "📊 Services Status:"
echo "   • Redis: Running on port 6379"
echo "   • Agent Memory Server: Running on port 8088"
echo ""
echo "🎯 You can now run the notebooks!"

