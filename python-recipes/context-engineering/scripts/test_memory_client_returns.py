#!/usr/bin/env python3
"""
Test script to check return types of agent-memory-client methods.
"""

import asyncio
import inspect
from agent_memory_client import MemoryAPIClient, MemoryClientConfig


async def main():
    """Check method signatures and return types."""
    
    # Get all methods from MemoryAPIClient
    methods = inspect.getmembers(MemoryAPIClient, predicate=inspect.isfunction)
    
    print("MemoryAPIClient methods:")
    print("=" * 80)
    
    for name, method in methods:
        if name.startswith('_'):
            continue
            
        sig = inspect.signature(method)
        print(f"\n{name}{sig}")
        
        # Try to get return annotation
        if sig.return_annotation != inspect.Signature.empty:
            print(f"  Returns: {sig.return_annotation}")


if __name__ == '__main__':
    asyncio.run(main())

