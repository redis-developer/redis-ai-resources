# Installation Guide

## Quick Installation

### From Source (Recommended for Development)

```bash
# Clone the repository
git clone https://github.com/redis-developer/redis-ai-resources.git
cd redis-ai-resources/python-recipes/context-engineering/reference-agent

# Install in development mode
pip install -e .

# Or install with development dependencies
pip install -e ".[dev]"
```

### From PyPI (When Available)

```bash
pip install redis-context-course
```

## Prerequisites

- Python 3.8 or higher
- Redis Stack (for vector search capabilities)
- OpenAI API key

## Setting up Redis

### Option 1: Docker (Recommended)

```bash
docker run -d --name redis-stack -p 6379:6379 redis/redis-stack:latest
```

### Option 2: Local Installation

Follow the [Redis Stack installation guide](https://redis.io/docs/stack/get-started/install/).

## Environment Configuration

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit `.env` and add your configuration:
```bash
OPENAI_API_KEY=your_openai_api_key_here
REDIS_URL=redis://localhost:6379
```

## Verification

Test that everything is working:

```bash
# Run the package tests
pytest tests/

# Generate sample data
generate-courses --courses-per-major 5 --output test_catalog.json

# Test Redis connection (requires Redis to be running)
python -c "from redis_context_course.redis_config import redis_config; print('Redis:', '✅' if redis_config.health_check() else '❌')"

# Start the interactive agent (requires OpenAI API key and Redis)
redis-class-agent --student-id test_user
```

## Troubleshooting

### Common Issues

1. **Import Error**: Make sure you installed the package with `pip install -e .`
2. **Redis Connection Failed**: Ensure Redis Stack is running on port 6379
3. **OpenAI API Error**: Check that your API key is set correctly in `.env`
4. **Permission Errors**: Use a virtual environment to avoid system-wide installation issues

### Getting Help

- Check the [README.md](README.md) for detailed usage instructions
- Review the [notebooks](../notebooks/) for examples
- Open an issue on [GitHub](https://github.com/redis-developer/redis-ai-resources/issues)

## Development Setup

For contributors and advanced users:

```bash
# Install with all development dependencies
pip install -e ".[dev,docs]"

# Run tests with coverage
pytest tests/ --cov=redis_context_course

# Format code
black redis_context_course/
isort redis_context_course/

# Type checking
mypy redis_context_course/

# Build documentation (if docs dependencies installed)
cd docs && make html
```
