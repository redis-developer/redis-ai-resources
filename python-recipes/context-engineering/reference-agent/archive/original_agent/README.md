# Original Agent Implementation (Archived)

This directory contains the original `ClassAgent` and `AugmentedClassAgent` implementations that were replaced by the progressive agent system.

## Archived Files

- **`agent.py`** - Original `ClassAgent` with full memory integration and tool calling
- **`augmented_agent.py`** - Enhanced agent with additional optimization features
- **`tools.py`** - Tool creation utilities for course search and memory management
- **`optimization_helpers.py`** - Context optimization and token management utilities
- **`cli.py`** - Original CLI implementation

## Why Archived?

These implementations were replaced with a **progressive learning system** that teaches students how to build agents incrementally:

1. **Stage 1: Baseline RAG** - Simple retrieval without optimization
2. **Stage 2: Context-Engineered** - Apply context engineering techniques
3. **Stage 3: Hybrid RAG** - Production-ready patterns with structured views

The new system is located in `../progressive_agents/`.

## Educational Value

The original agent was a complete, production-ready implementation that demonstrated all concepts at once. While powerful, it was difficult for students to understand the progression from basic to advanced patterns.

The progressive agent system breaks down the same concepts into digestible stages, allowing students to:
- See the evolution from naive to optimized approaches
- Understand the impact of each optimization technique
- Make informed decisions about trade-offs
- Build confidence through incremental complexity

## Using the Archived Code

If you need to reference the original implementation:

```python
# This code is archived and not maintained
# For current implementations, see ../progressive_agents/

from archive.original_agent.agent import ClassAgent
from archive.original_agent.tools import create_course_tools, create_memory_tools
```

## Migration Notes

The core infrastructure (CourseManager, redis_config, models) remains unchanged and is still actively used by both the notebooks and the progressive agent system.

Only the agent implementations and CLI were archived.

