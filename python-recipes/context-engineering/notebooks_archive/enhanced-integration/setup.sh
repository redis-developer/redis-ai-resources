#!/bin/bash

# Setup script for Progressive Context Engineering Notebooks
# Run this once before starting the notebooks

set -e  # Exit on any error

echo "🚀 Progressive Context Engineering Setup"
echo "========================================"

# Check if we're in the right directory
if [ ! -d "section-1-fundamentals" ]; then
    echo "❌ Error: Please run this script from the enhanced-integration directory"
    echo "   Expected to find: section-1-fundamentals/"
    exit 1
fi

echo "📋 Step 1: Installing Reference Agent"
echo "------------------------------------"
if [ ! -d "../../reference-agent" ]; then
    echo "❌ Reference agent not found at ../../reference-agent"
    echo "   Please ensure the reference-agent directory exists"
    exit 1
fi

echo "Installing reference agent in editable mode..."
pip install -e ../../reference-agent
echo "✅ Reference agent installed"

echo ""
echo "📋 Step 2: Installing Dependencies"
echo "----------------------------------"
echo "Installing required packages..."
pip install python-dotenv jupyter nbformat redis openai langchain langchain-openai langchain-core scikit-learn numpy pandas
echo "✅ Dependencies installed"

echo ""
echo "📋 Step 3: Setting Up Environment File"
echo "--------------------------------------"
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "✅ Created .env file from template"
    else
        echo "❌ .env.example not found"
        exit 1
    fi
else
    echo "⚠️  .env file already exists - keeping existing file"
fi

echo ""
echo "📋 Step 4: Testing Installation"
echo "-------------------------------"
python3 -c "
try:
    import redis_context_course.models
    import dotenv
    import openai
    import langchain
    print('✅ All imports successful')
except ImportError as e:
    print(f'❌ Import failed: {e}')
    exit(1)
"

echo ""
echo "🎉 Setup Complete!"
echo "=================="
echo ""
echo "Next steps:"
echo "1. 📝 Edit .env file and add your OpenAI API key"
echo "   Get key from: https://platform.openai.com/api-keys"
echo ""
echo "2. 🚀 Start learning:"
echo "   jupyter notebook"
echo ""
echo "3. 🔧 Optional - Start Redis:"
echo "   docker run -d -p 6379:6379 -p 8001:8001 redis/redis-stack"
echo ""
echo "📚 Begin with: section-1-fundamentals/01_context_engineering_overview.ipynb"
echo ""
echo "Happy learning! 🎓"
