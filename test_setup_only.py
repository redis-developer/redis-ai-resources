#!/usr/bin/env python3
"""
Test script to verify setup without requiring OpenAI API key

This script checks:
1. Redis connection
2. Required Python packages
3. Agent code can be imported
4. Basic functionality without LLM calls
"""

import os
import sys
import subprocess
from pathlib import Path

def check_redis():
    """Check Redis connection"""
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, decode_responses=True)
        r.ping()
        print("✅ Redis is running")
        return True
    except Exception as e:
        print(f"❌ Redis connection failed: {e}")
        return False

def check_packages():
    """Check required packages"""
    required_packages = [
        'langchain', 'langchain_openai', 'langchain_redis', 
        'langgraph', 'redisvl', 'redis', 'pydantic'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package}")
            missing.append(package)
    
    return len(missing) == 0

def test_oregon_trail_import():
    """Test if Oregon Trail agent can be imported"""
    try:
        sys.path.append('nk_scripts')
        from full_featured_agent import OregonTrailAgent, ToolManager
        print("✅ Oregon Trail Agent can be imported")
        
        # Test basic tool functionality without LLM
        from full_featured_agent import restock_tool
        result = restock_tool(10, 3, 50)  # daily_usage=10, lead_time=3, safety_stock=50
        expected = (10 * 3) + 50  # 80
        
        if result == expected:
            print(f"✅ Restock tool works correctly: {result}")
            return True
        else:
            print(f"❌ Restock tool failed: expected {expected}, got {result}")
            return False
            
    except Exception as e:
        print(f"❌ Oregon Trail Agent import failed: {e}")
        return False

def test_context_agent_import():
    """Test if Context Course Agent can be imported"""
    try:
        from redis_context_course import ClassAgent, CourseManager
        print("✅ Context Course Agent can be imported")
        return True
    except Exception as e:
        print(f"❌ Context Course Agent import failed: {e}")
        print("   This is expected if the package isn't installed yet")
        return False

def test_redis_operations():
    """Test basic Redis operations"""
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, decode_responses=True)
        
        # Test basic operations
        r.set('test_key', 'test_value')
        value = r.get('test_key')
        r.delete('test_key')
        
        if value == 'test_value':
            print("✅ Redis basic operations work")
            return True
        else:
            print("❌ Redis basic operations failed")
            return False
            
    except Exception as e:
        print(f"❌ Redis operations failed: {e}")
        return False

def main():
    """Main test function"""
    print("🔧 Redis AI Reference Agents - Setup Verification")
    print("="*60)
    
    tests = [
        ("Redis Connection", check_redis),
        ("Required Packages", check_packages),
        ("Redis Operations", test_redis_operations),
        ("Oregon Trail Agent Import", test_oregon_trail_import),
        ("Context Course Agent Import", test_context_agent_import),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🔍 Testing {test_name}...")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*60)
    print("📊 SETUP VERIFICATION SUMMARY")
    print("="*60)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nPassed: {passed}/{len(results)} tests")
    
    if passed == len(results):
        print("\n🎉 Perfect! All setup tests passed!")
        print("Next steps:")
        print("1. Set your OpenAI API key: export OPENAI_API_KEY='your-key-here'")
        print("2. Run: python test_reference_agents.py")
    elif passed >= 3:  # Redis, packages, and basic operations
        print("\n✅ Core setup is working!")
        print("Next steps:")
        print("1. Set your OpenAI API key: export OPENAI_API_KEY='your-key-here'")
        print("2. For Context Course Agent, run: cd python-recipes/context-engineering/reference-agent && pip install -e .")
        print("3. Run: python test_reference_agents.py")
    else:
        print("\n❌ Setup issues detected. Please fix the failed tests above.")
    
    print("\n🏁 Setup verification complete!")

if __name__ == "__main__":
    main()
