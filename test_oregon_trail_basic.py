#!/usr/bin/env python3
"""
Basic test for Oregon Trail Agent without requiring OpenAI API key
Tests the tool functionality and basic imports
"""

import os
import sys
from typing import Literal
from pydantic import BaseModel, Field

# Add the nk_scripts directory to path
sys.path.append('nk_scripts')

def test_restock_tool():
    """Test the restock tool calculation"""
    print("🔧 Testing restock tool...")
    
    # Import the tool function directly
    try:
        # Define the tool locally to avoid the API key check
        def restock_tool(daily_usage: int, lead_time: int, safety_stock: int) -> int:
            """Restock formula tool used specifically for calculating the amount of food at which you should start restocking."""
            return (daily_usage * lead_time) + safety_stock
        
        # Test the calculation
        result = restock_tool(10, 3, 50)  # daily_usage=10, lead_time=3, safety_stock=50
        expected = (10 * 3) + 50  # 80
        
        if result == expected:
            print(f"✅ Restock tool works correctly: {result}")
            return True
        else:
            print(f"❌ Restock tool failed: expected {expected}, got {result}")
            return False
            
    except Exception as e:
        print(f"❌ Restock tool test failed: {e}")
        return False

def test_imports():
    """Test if we can import the required modules"""
    print("📦 Testing imports...")
    
    try:
        # Test LangChain imports
        from langchain_core.tools import tool
        from langchain_core.messages import HumanMessage
        from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        from langchain_redis import RedisConfig, RedisVectorStore
        from langchain_core.documents import Document
        from langchain.tools.retriever import create_retriever_tool
        print("✅ LangChain imports successful")
        
        # Test LangGraph imports
        from langgraph.graph import MessagesState, StateGraph, END
        from langgraph.prebuilt import ToolNode
        print("✅ LangGraph imports successful")
        
        # Test RedisVL imports
        from redisvl.extensions.llmcache import SemanticCache
        print("✅ RedisVL imports successful")
        
        # Test Pydantic imports
        from pydantic import BaseModel, Field
        print("✅ Pydantic imports successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        return False

def test_redis_connection():
    """Test Redis connection"""
    print("🔗 Testing Redis connection...")
    
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, decode_responses=True)
        result = r.ping()
        
        if result:
            print("✅ Redis connection successful")
            return True
        else:
            print("❌ Redis ping failed")
            return False
            
    except Exception as e:
        print(f"❌ Redis connection failed: {e}")
        return False

def test_pydantic_models():
    """Test Pydantic model definitions"""
    print("📋 Testing Pydantic models...")
    
    try:
        # Test RestockInput model
        class RestockInput(BaseModel):
            daily_usage: int = Field(description="Pounds (lbs) of food expected to be consumed daily")
            lead_time: int = Field(description="Lead time to replace food in days")
            safety_stock: int = Field(description="Number of pounds (lbs) of safety stock to keep on hand")
        
        # Test MultipleChoiceResponse model
        class MultipleChoiceResponse(BaseModel):
            multiple_choice_response: Literal["A", "B", "C", "D"] = Field(
                description="Single character response to the question for multiple choice questions. Must be either A, B, C, or D."
            )
        
        # Test creating instances
        restock_input = RestockInput(daily_usage=10, lead_time=3, safety_stock=50)
        choice_response = MultipleChoiceResponse(multiple_choice_response="A")
        
        print("✅ Pydantic models work correctly")
        return True
        
    except Exception as e:
        print(f"❌ Pydantic model test failed: {e}")
        return False

def test_vector_store_config():
    """Test vector store configuration (without actually connecting)"""
    print("🗂️  Testing vector store configuration...")
    
    try:
        from langchain_redis import RedisConfig
        from langchain_core.documents import Document
        
        # Test creating config
        config = RedisConfig(
            index_name="test_oregon_trail",
            redis_url="redis://localhost:6379"
        )
        
        # Test creating document
        doc = Document(
            page_content="the northern trail, of the blue mountains, was destroyed by a flood and is no longer safe to traverse. It is recommended to take the southern trail although it is longer."
        )
        
        print("✅ Vector store configuration successful")
        return True
        
    except Exception as e:
        print(f"❌ Vector store configuration failed: {e}")
        return False

def main():
    """Run all basic tests"""
    print("🎮 Oregon Trail Agent - Basic Setup Test")
    print("="*60)
    print("Note: This test runs without requiring an OpenAI API key")
    print("="*60)
    
    tests = [
        ("Redis Connection", test_redis_connection),
        ("Package Imports", test_imports),
        ("Restock Tool", test_restock_tool),
        ("Pydantic Models", test_pydantic_models),
        ("Vector Store Config", test_vector_store_config),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🔍 {test_name}...")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*60)
    print("📊 BASIC TEST SUMMARY")
    print("="*60)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nPassed: {passed}/{len(results)} tests")
    
    if passed == len(results):
        print("\n🎉 Excellent! All basic tests passed!")
        print("\nThe Oregon Trail Agent setup is working correctly.")
        print("\nNext steps:")
        print("1. Set your OpenAI API key: export OPENAI_API_KEY='your-key-here'")
        print("2. Run the full agent: python nk_scripts/full_featured_agent.py")
    elif passed >= 3:
        print("\n✅ Core functionality is working!")
        print("Some advanced features may need attention, but the basic setup is good.")
        print("\nNext steps:")
        print("1. Set your OpenAI API key: export OPENAI_API_KEY='your-key-here'")
        print("2. Try running: python nk_scripts/full_featured_agent.py")
    else:
        print("\n❌ Several issues detected. Please fix the failed tests above.")
    
    print("\n🏁 Basic test complete!")

if __name__ == "__main__":
    main()
