#!/usr/bin/env python3
"""
Quick test to verify the notebook fixes work correctly.
"""

import asyncio
from dotenv import load_dotenv

load_dotenv("reference-agent/.env")

async def test_imports():
    """Test that all imports work correctly."""
    print("Testing imports...")
    
    try:
        from agent_memory_client.filters import UserId, MemoryType
        print("✅ UserId and MemoryType imported from filters")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    
    try:
        from agent_memory_client import MemoryAPIClient
        from agent_memory_client.config import MemoryClientConfig
        print("✅ MemoryAPIClient and MemoryClientConfig imported")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    
    return True

async def test_user_id_filter():
    """Test that UserId filter works correctly."""
    print("\nTesting UserId filter...")
    
    try:
        from agent_memory_client.filters import UserId
        
        # Test creating a UserId filter
        user_filter = UserId(eq="test_user")
        print(f"✅ Created UserId filter: {user_filter}")
        
        # Test that it has model_dump method
        if hasattr(user_filter, 'model_dump'):
            print("✅ UserId has model_dump method")
        else:
            print("❌ UserId missing model_dump method")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True

async def test_memory_type_filter():
    """Test that MemoryType filter works correctly."""
    print("\nTesting MemoryType filter...")
    
    try:
        from agent_memory_client.filters import MemoryType
        
        # Test creating a MemoryType filter
        type_filter = MemoryType(eq="semantic")
        print(f"✅ Created MemoryType filter: {type_filter}")
        
        # Test that it has model_dump method
        if hasattr(type_filter, 'model_dump'):
            print("✅ MemoryType has model_dump method")
        else:
            print("❌ MemoryType missing model_dump method")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True

async def main():
    """Run all tests."""
    print("=" * 60)
    print("Testing Notebook Fixes")
    print("=" * 60)
    
    results = []
    
    results.append(await test_imports())
    results.append(await test_user_id_filter())
    results.append(await test_memory_type_filter())
    
    print("\n" + "=" * 60)
    if all(results):
        print("✅ All tests passed!")
        print("=" * 60)
        return 0
    else:
        print("❌ Some tests failed")
        print("=" * 60)
        return 1

if __name__ == "__main__":
    exit(asyncio.run(main()))

