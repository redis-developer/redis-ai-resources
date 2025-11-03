#!/usr/bin/env python3
"""
Test script to verify the full setup of the Redis Context Course agent.
This script tests all components including OpenAI integration.
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def check_environment():
    """Check if all required environment variables are set."""
    print("🔍 Checking environment variables...")
    
    required_vars = {
        'OPENAI_API_KEY': 'OpenAI API key for embeddings and chat',
        'REDIS_URL': 'Redis connection URL',
        'AGENT_MEMORY_URL': 'Agent Memory Server URL'
    }
    
    missing_vars = []
    for var, description in required_vars.items():
        value = os.getenv(var)
        if not value or value == 'your_openai_api_key_here':
            print(f"❌ {var}: Not set or using placeholder")
            missing_vars.append(var)
        else:
            # Mask API key for security
            if 'API_KEY' in var:
                masked_value = value[:8] + '...' + value[-4:] if len(value) > 12 else '***'
                print(f"✅ {var}: {masked_value}")
            else:
                print(f"✅ {var}: {value}")
    
    if missing_vars:
        print(f"\n❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("Please update your .env file with the correct values.")
        return False
    
    print("✅ All environment variables are set!")
    return True

async def test_redis_connection():
    """Test Redis connection."""
    print("\n🔗 Testing Redis connection...")
    try:
        from redis_context_course.redis_config import get_redis_client
        redis_client = get_redis_client()
        await redis_client.ping()
        print("✅ Redis connection successful!")
        return True
    except Exception as e:
        print(f"❌ Redis connection failed: {e}")
        return False

async def test_openai_connection():
    """Test OpenAI API connection."""
    print("\n🤖 Testing OpenAI API connection...")
    try:
        from openai import OpenAI
        client = OpenAI()
        
        # Test with a simple embedding request
        response = client.embeddings.create(
            model="text-embedding-ada-002",
            input="test"
        )
        print("✅ OpenAI API connection successful!")
        return True
    except Exception as e:
        print(f"❌ OpenAI API connection failed: {e}")
        return False

async def test_course_ingestion():
    """Test course data ingestion."""
    print("\n📚 Testing course data ingestion...")
    try:
        # Check if course_catalog.json exists
        if not os.path.exists('course_catalog.json'):
            print("❌ course_catalog.json not found. Run 'generate-courses' first.")
            return False
        
        # Try to ingest a small sample
        print("Attempting to ingest course data...")
        import subprocess
        result = subprocess.run(
            ['ingest-courses', '--catalog', 'course_catalog.json', '--clear'],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0 and "✅ Ingested" in result.stdout:
            print("✅ Course data ingestion successful!")
            return True
        else:
            print(f"❌ Course ingestion failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Course ingestion test failed: {e}")
        return False

async def test_agent_initialization():
    """Test agent initialization."""
    print("\n🤖 Testing agent initialization...")
    try:
        from redis_context_course import ClassAgent
        agent = ClassAgent("test_student")
        print("✅ Agent initialization successful!")
        return True
    except Exception as e:
        print(f"❌ Agent initialization failed: {e}")
        return False

async def test_basic_chat():
    """Test basic chat functionality."""
    print("\n💬 Testing basic chat functionality...")
    try:
        from redis_context_course import ClassAgent
        agent = ClassAgent("test_student")
        
        # Test a simple query
        response = await agent.chat("Hello, can you help me find courses?")
        
        if response and len(response) > 0:
            print("✅ Basic chat functionality working!")
            print(f"Sample response: {response[:100]}...")
            return True
        else:
            print("❌ Chat returned empty response")
            return False
    except Exception as e:
        print(f"❌ Chat functionality test failed: {e}")
        return False

async def main():
    """Run all tests."""
    print("🎓 Redis Context Course - Full Setup Test")
    print("=" * 50)
    
    tests = [
        ("Environment Check", check_environment),
        ("Redis Connection", test_redis_connection),
        ("OpenAI Connection", test_openai_connection),
        ("Course Ingestion", test_course_ingestion),
        ("Agent Initialization", test_agent_initialization),
        ("Basic Chat", test_basic_chat),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            results[test_name] = result
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results[test_name] = False
        
        # Stop if environment check fails
        if test_name == "Environment Check" and not results[test_name]:
            break
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} {test_name}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your setup is ready to use.")
        print("\nNext steps:")
        print("1. Try the interactive CLI: redis-class-agent --student-id your_name")
        print("2. Explore the Python API with the examples")
        print("3. Check out the notebooks for detailed tutorials")
    else:
        print("⚠️  Some tests failed. Please check the errors above and fix the issues.")
        return 1
    
    return 0

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⏹️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test script failed: {e}")
        sys.exit(1)
