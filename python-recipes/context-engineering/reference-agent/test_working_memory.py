#!/usr/bin/env python3
"""
Test script for working memory with extraction strategies.
"""

import asyncio
import os
from langchain_core.messages import HumanMessage, AIMessage

# Set up environment
os.environ.setdefault("OPENAI_API_KEY", "sk-dummy-key-for-testing")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379")

from redis_context_course.working_memory import WorkingMemory, MessageCountStrategy
from redis_context_course.memory import MemoryManager
from redis_context_course.working_memory_tools import WorkingMemoryToolProvider


async def test_working_memory():
    """Test working memory with extraction strategy."""
    print("🧠 Testing Working Memory with Extraction Strategy")
    print("=" * 60)
    
    # Initialize components
    student_id = "test_student_working_memory"
    strategy = MessageCountStrategy(message_threshold=5, min_importance=0.6)
    working_memory = WorkingMemory(student_id, strategy)
    memory_manager = MemoryManager(student_id)
    tool_provider = WorkingMemoryToolProvider(working_memory, memory_manager)
    
    print(f"📊 Initial state:")
    print(f"   Strategy: {strategy.name}")
    print(f"   Trigger: {strategy.trigger_condition}")
    print(f"   Priority: {strategy.priority_criteria}")
    print(f"   Items in working memory: {len(working_memory.items)}")
    print()
    
    # Add some messages to working memory
    messages = [
        HumanMessage(content="I prefer online courses because I work part-time"),
        AIMessage(content="I understand you prefer online courses due to your work schedule. That's a great preference to keep in mind."),
        HumanMessage(content="My goal is to specialize in machine learning"),
        AIMessage(content="Machine learning is an excellent specialization! I can help you find relevant courses."),
        HumanMessage(content="What courses do you recommend for AI?"),
        AIMessage(content="For AI, I'd recommend starting with CS301: Machine Learning Fundamentals, then CS401: Deep Learning."),
    ]
    
    print("📝 Adding messages to working memory...")
    for i, message in enumerate(messages, 1):
        working_memory.add_message(message)
        print(f"   {i}. Added {type(message).__name__}: {message.content[:50]}...")
        print(f"      Should extract: {working_memory.should_extract_to_long_term()}")
    
    print()
    print(f"📊 Working memory status:")
    print(f"   Items: {len(working_memory.items)}")
    print(f"   Should extract: {working_memory.should_extract_to_long_term()}")
    
    # Test extraction
    if working_memory.should_extract_to_long_term():
        print("\n🔄 Extraction triggered! Extracting memories...")
        extracted_memories = working_memory.extract_to_long_term()
        
        print(f"   Extracted {len(extracted_memories)} memories:")
        for i, memory in enumerate(extracted_memories, 1):
            print(f"   {i}. [{memory.memory_type}] {memory.content[:60]}... (importance: {memory.importance:.2f})")
        
        # Store in long-term memory
        print("\n💾 Storing extracted memories in long-term storage...")
        for memory in extracted_memories:
            try:
                memory_id = await memory_manager.store_memory(
                    content=memory.content,
                    memory_type=memory.memory_type,
                    importance=memory.importance,
                    metadata=memory.metadata
                )
                print(f"   ✅ Stored: {memory_id[:8]}...")
            except Exception as e:
                print(f"   ❌ Error: {e}")
    
    print(f"\n📊 Final working memory status:")
    print(f"   Items remaining: {len(working_memory.items)}")
    print(f"   Last extraction: {working_memory.last_extraction}")
    
    # Test working memory tools
    print("\n🛠️  Testing Working Memory Tools")
    print("-" * 40)
    
    tools = tool_provider.get_memory_tool_schemas()
    print(f"Available tools: {[tool.name for tool in tools]}")
    
    # Test get_working_memory_status tool
    status_tool = next(tool for tool in tools if tool.name == "get_working_memory_status")
    status = await status_tool.ainvoke({})
    print(f"\n📊 Working Memory Status Tool Output:")
    print(status)
    
    # Test strategy context for system prompt
    print("\n🎯 Strategy Context for System Prompt:")
    context = tool_provider.get_strategy_context_for_system_prompt()
    print(context)
    
    print("\n✅ Working memory test completed!")


async def test_memory_tools():
    """Test the working memory tools."""
    print("\n🛠️  Testing Memory Tools with Strategy Awareness")
    print("=" * 60)
    
    # Initialize components
    student_id = "test_student_tools"
    strategy = MessageCountStrategy(message_threshold=3, min_importance=0.5)
    working_memory = WorkingMemory(student_id, strategy)
    memory_manager = MemoryManager(student_id)
    tool_provider = WorkingMemoryToolProvider(working_memory, memory_manager)
    
    tools = tool_provider.get_memory_tool_schemas()
    
    # Test add_memories_to_working_memory
    add_memories_tool = next(tool for tool in tools if tool.name == "add_memories_to_working_memory")
    
    print("📝 Testing add_memories_to_working_memory...")
    result = await add_memories_tool.ainvoke({
        "memories": [
            "Student prefers evening classes",
            "Interested in data science track",
            "Has programming experience in Python"
        ],
        "memory_type": "preference"
    })
    print(f"Result: {result}")
    
    # Test create_memory
    create_memory_tool = next(tool for tool in tools if tool.name == "create_memory")
    
    print("\n📝 Testing create_memory...")
    result = await create_memory_tool.ainvoke({
        "content": "Student's goal is to become a data scientist",
        "memory_type": "goal",
        "importance": 0.9
    })
    print(f"Result: {result}")
    
    # Test status
    status_tool = next(tool for tool in tools if tool.name == "get_working_memory_status")
    status = await status_tool.ainvoke({})
    print(f"\n📊 Final Status:")
    print(status)
    
    print("\n✅ Memory tools test completed!")


async def main():
    """Run all tests."""
    try:
        await test_working_memory()
        await test_memory_tools()
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
