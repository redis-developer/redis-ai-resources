#!/bin/bash

# Notebook Validation Script for Section 5
# This script validates all notebooks in Section 5 by executing them and checking for errors

set -e  # Exit on error

echo "=========================================="
echo "Section 5 Notebook Validation"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check environment variables
echo "📋 Step 1: Checking Environment Variables..."
echo ""

if [ -z "$OPENAI_API_KEY" ]; then
    echo -e "${RED}❌ OPENAI_API_KEY not set${NC}"
    echo "   Please set your OpenAI API key:"
    echo "   export OPENAI_API_KEY='your-key-here'"
    echo ""
    echo "   Or load from .env file:"
    echo "   cd ../../ && source .env"
    exit 1
else
    echo -e "${GREEN}✅ OPENAI_API_KEY is set${NC}"
fi

REDIS_URL=${REDIS_URL:-redis://localhost:6379}
AGENT_MEMORY_URL=${AGENT_MEMORY_URL:-http://localhost:8000}

echo -e "${GREEN}✅ Redis URL: $REDIS_URL${NC}"
echo -e "${GREEN}✅ Agent Memory URL: $AGENT_MEMORY_URL${NC}"
echo ""

# Check Redis connection
echo "📋 Step 2: Checking Redis Connection..."
echo ""

if command -v redis-cli &> /dev/null; then
    if redis-cli -u "$REDIS_URL" ping &> /dev/null; then
        echo -e "${GREEN}✅ Redis is running and accessible${NC}"
    else
        echo -e "${RED}❌ Redis is not accessible at $REDIS_URL${NC}"
        echo "   Please start Redis:"
        echo "   docker run -d -p 6379:6379 redis/redis-stack:latest"
        exit 1
    fi
else
    echo -e "${YELLOW}⚠️  redis-cli not found, skipping Redis check${NC}"
fi
echo ""

# Check Agent Memory Server
echo "📋 Step 3: Checking Agent Memory Server..."
echo ""

if curl -s "$AGENT_MEMORY_URL/health" &> /dev/null; then
    echo -e "${GREEN}✅ Agent Memory Server is running${NC}"
else
    echo -e "${RED}❌ Agent Memory Server is not accessible at $AGENT_MEMORY_URL${NC}"
    echo "   Please start Agent Memory Server:"
    echo "   docker run -d -p 8000:8000 redis/agent-memory-server:latest"
    exit 1
fi
echo ""

# Check Python dependencies
echo "📋 Step 4: Checking Python Dependencies..."
echo ""

python3 -c "import langchain_openai" 2>/dev/null && echo -e "${GREEN}✅ langchain-openai${NC}" || echo -e "${RED}❌ langchain-openai${NC}"
python3 -c "import langgraph" 2>/dev/null && echo -e "${GREEN}✅ langgraph${NC}" || echo -e "${RED}❌ langgraph${NC}"
python3 -c "import redisvl" 2>/dev/null && echo -e "${GREEN}✅ redisvl${NC}" || echo -e "${RED}❌ redisvl${NC}"
python3 -c "import agent_memory_client" 2>/dev/null && echo -e "${GREEN}✅ agent-memory-client${NC}" || echo -e "${RED}❌ agent-memory-client${NC}"
python3 -c "import tiktoken" 2>/dev/null && echo -e "${GREEN}✅ tiktoken${NC}" || echo -e "${RED}❌ tiktoken${NC}"
echo ""

# Execute notebooks
echo "=========================================="
echo "📓 Executing Notebooks"
echo "=========================================="
echo ""

NOTEBOOKS=(
    "01_measuring_optimizing_performance.ipynb"
    "02_scaling_semantic_tool_selection.ipynb"
    "03_production_readiness_quality_assurance.ipynb"
)

FAILED_NOTEBOOKS=()
PASSED_NOTEBOOKS=()

for notebook in "${NOTEBOOKS[@]}"; do
    echo "=========================================="
    echo "📓 Executing: $notebook"
    echo "=========================================="
    echo ""
    
    # Execute notebook
    if jupyter nbconvert --to notebook --execute "$notebook" \
        --output "${notebook%.ipynb}_executed.ipynb" \
        --ExecutePreprocessor.timeout=600 \
        --ExecutePreprocessor.kernel_name=python3 2>&1 | tee "${notebook%.ipynb}_execution.log"; then
        
        echo ""
        echo -e "${GREEN}✅ SUCCESS: $notebook executed without errors${NC}"
        PASSED_NOTEBOOKS+=("$notebook")
        
        # Clean up executed notebook (keep original)
        rm -f "${notebook%.ipynb}_executed.ipynb"
    else
        echo ""
        echo -e "${RED}❌ FAILED: $notebook had execution errors${NC}"
        echo "   Check log: ${notebook%.ipynb}_execution.log"
        FAILED_NOTEBOOKS+=("$notebook")
    fi
    
    echo ""
done

# Summary
echo "=========================================="
echo "📊 Validation Summary"
echo "=========================================="
echo ""

echo "Passed: ${#PASSED_NOTEBOOKS[@]}/${#NOTEBOOKS[@]}"
for notebook in "${PASSED_NOTEBOOKS[@]}"; do
    echo -e "  ${GREEN}✅ $notebook${NC}"
done

if [ ${#FAILED_NOTEBOOKS[@]} -gt 0 ]; then
    echo ""
    echo "Failed: ${#FAILED_NOTEBOOKS[@]}/${#NOTEBOOKS[@]}"
    for notebook in "${FAILED_NOTEBOOKS[@]}"; do
        echo -e "  ${RED}❌ $notebook${NC}"
    done
    echo ""
    echo -e "${RED}❌ Validation FAILED${NC}"
    exit 1
else
    echo ""
    echo -e "${GREEN}✅ All notebooks validated successfully!${NC}"
    exit 0
fi

