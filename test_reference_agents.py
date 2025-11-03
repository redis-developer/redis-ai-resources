#!/usr/bin/env python3
"""
Test script for Redis AI Reference Agents

This script helps you test both reference agents:
1. Oregon Trail Agent (simple tool-calling agent)
2. Context Course Agent (complex memory-based agent)

Prerequisites:
- Redis running on localhost:6379
- OpenAI API key set as environment variable
- Required Python packages installed
"""

import os
import sys
import subprocess
from pathlib import Path

def check_prerequisites():
    """Check if all prerequisites are met"""
    print("🔍 Checking prerequisites...")
    
    # Check Redis connection
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, decode_responses=True)
        r.ping()
        print("✅ Redis is running")
    except Exception as e:
        print(f"❌ Redis connection failed: {e}")
        print("   Please start Redis: docker run -d --name redis -p 6379:6379 redis:8-alpine")
        return False
    
    # Check OpenAI API key
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ OpenAI API key not set")
        print("   Please set: export OPENAI_API_KEY='your-key-here'")
        return False
    else:
        print("✅ OpenAI API key is set")
    
    # Check required packages
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
    
    if missing:
        print(f"\n❌ Missing packages: {missing}")
        print("   Install with: pip install " + " ".join(missing))
        return False
    
    print("\n🎉 All prerequisites met!")
    return True

def test_oregon_trail_agent():
    """Test the Oregon Trail Agent"""
    print("\n" + "="*60)
    print("🎮 Testing Oregon Trail Agent")
    print("="*60)
    
    try:
        # Import and run the agent
        sys.path.append('nk_scripts')
        from full_featured_agent import OregonTrailAgent, run_scenario
        
        # Create agent
        agent = OregonTrailAgent()
        
        # Test a simple scenario
        test_scenario = {
            "name": "Quick Test",
            "question": "What is the first name of the wagon leader?",
            "answer": "Art",
            "type": "free-form"
        }
        
        print("Running quick test scenario...")
        success = run_scenario(agent, test_scenario)
        
        if success:
            print("✅ Oregon Trail Agent test passed!")
            return True
        else:
            print("❌ Oregon Trail Agent test failed!")
            return False
            
    except Exception as e:
        print(f"❌ Oregon Trail Agent test failed with error: {e}")
        return False

def test_context_course_agent():
    """Test the Context Course Agent"""
    print("\n" + "="*60)
    print("🎓 Testing Context Course Agent")
    print("="*60)
    
    try:
        # Check if the agent is installed
        result = subprocess.run(['redis-class-agent', '--help'], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ Context Course Agent CLI is available")
            print("   You can run it with: redis-class-agent --student-id test_student")
            return True
        else:
            print("❌ Context Course Agent CLI not found")
            print("   Install with: cd python-recipes/context-engineering/reference-agent && pip install -e .")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Context Course Agent CLI test timed out")
        return False
    except FileNotFoundError:
        print("❌ Context Course Agent CLI not found")
        print("   Install with: cd python-recipes/context-engineering/reference-agent && pip install -e .")
        return False
    except Exception as e:
        print(f"❌ Context Course Agent test failed with error: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Redis AI Reference Agents Test Suite")
    print("="*60)
    
    # Check prerequisites
    if not check_prerequisites():
        print("\n❌ Prerequisites not met. Please fix the issues above and try again.")
        sys.exit(1)
    
    # Test Oregon Trail Agent
    oregon_success = test_oregon_trail_agent()
    
    # Test Context Course Agent
    context_success = test_context_course_agent()
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    print(f"Oregon Trail Agent: {'✅ PASS' if oregon_success else '❌ FAIL'}")
    print(f"Context Course Agent: {'✅ PASS' if context_success else '❌ FAIL'}")
    
    if oregon_success and context_success:
        print("\n🎉 All tests passed! Both reference agents are working.")
    elif oregon_success:
        print("\n⚠️  Oregon Trail Agent works, but Context Course Agent needs setup.")
        print("   See instructions above for Context Course Agent setup.")
    elif context_success:
        print("\n⚠️  Context Course Agent works, but Oregon Trail Agent failed.")
        print("   Check the error messages above for Oregon Trail Agent.")
    else:
        print("\n❌ Both agents failed. Check the error messages above.")
    
    print("\n🏁 Test complete!")

if __name__ == "__main__":
    main()
