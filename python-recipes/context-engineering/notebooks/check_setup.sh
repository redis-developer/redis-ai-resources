#!/bin/bash
# Quick setup checker for Context Engineering notebooks
# This script checks if required services are running

echo "🔍 Context Engineering Setup Checker"
echo "====================================="

# Check if Docker is running
echo "📊 Checking Docker..."
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running"
    echo "   Please start Docker Desktop and try again"
    exit 1
else
    echo "✅ Docker is running"
fi

# Check if Redis is running
echo "📊 Checking Redis..."
if docker ps --filter name=redis-stack-server --format '{{.Names}}' | grep -q redis-stack-server; then
    echo "✅ Redis is running"
    REDIS_OK=true
else
    echo "❌ Redis is not running"
    echo "   Run: docker run -d --name redis-stack-server -p 6379:6379 redis/redis-stack-server:latest"
    REDIS_OK=false
fi

# Check if Agent Memory Server is running
echo "📊 Checking Agent Memory Server..."
if docker ps --filter name=agent-memory-server --format '{{.Names}}' | grep -q agent-memory-server; then
    if curl -s http://localhost:8088/v1/health > /dev/null 2>&1; then
        echo "✅ Agent Memory Server is running and healthy"
        MEMORY_OK=true
    else
        echo "⚠️  Agent Memory Server container exists but not responding"
        MEMORY_OK=false
    fi
else
    echo "❌ Agent Memory Server is not running"
    echo "   Run: ./setup_memory_server.sh (requires OPENAI_API_KEY)"
    MEMORY_OK=false
fi

# Check environment file
echo "📊 Checking environment configuration..."
if [ -f "../reference-agent/.env" ]; then
    if grep -q "OPENAI_API_KEY=" "../reference-agent/.env"; then
        echo "✅ Environment file exists with API key"
        ENV_OK=true
    else
        echo "⚠️  Environment file exists but missing OPENAI_API_KEY"
        ENV_OK=false
    fi
else
    echo "❌ Environment file not found"
    echo "   Create: ../reference-agent/.env with OPENAI_API_KEY=your_key_here"
    ENV_OK=false
fi

echo ""
echo "📋 Setup Status Summary:"
echo "========================"
echo "Docker:              $([ "$REDIS_OK" = true ] && echo "✅" || echo "❌")"
echo "Redis:               $([ "$REDIS_OK" = true ] && echo "✅" || echo "❌")"
echo "Agent Memory Server: $([ "$MEMORY_OK" = true ] && echo "✅" || echo "❌")"
echo "Environment:         $([ "$ENV_OK" = true ] && echo "✅" || echo "❌")"

if [ "$REDIS_OK" = true ] && [ "$MEMORY_OK" = true ] && [ "$ENV_OK" = true ]; then
    echo ""
    echo "🎉 All systems ready! You can run the notebooks."
    exit 0
else
    echo ""
    echo "⚠️  Some services need attention. See messages above."
    echo "📖 For detailed setup: see SETUP_GUIDE.md"
    exit 1
fi
