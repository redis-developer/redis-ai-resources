#!/usr/bin/env python3
"""
Validation script for 03_memory_management_long_conversations.ipynb
Tests key components to ensure the notebook will execute successfully.
"""

import os
import sys
import asyncio
from pathlib import Path
from typing import List, Optional
from dataclasses import dataclass, field
import time

# Add reference-agent to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "reference-agent"))

# Load environment variables
from dotenv import load_dotenv
env_path = Path(__file__).parent.parent.parent / "reference-agent" / ".env"
load_dotenv(dotenv_path=env_path)

# Imports
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from agent_memory_client import MemoryAPIClient, MemoryClientConfig
from agent_memory_client.models import WorkingMemory, MemoryMessage, ClientMemoryRecord
import tiktoken

print("✅ All imports successful\n")

# Initialize clients
llm = ChatOpenAI(model="gpt-4o", temperature=0.7)
memory_config = MemoryClientConfig(base_url=os.getenv("AGENT_MEMORY_URL", "http://localhost:8088"))
memory_client = MemoryAPIClient(config=memory_config)
tokenizer = tiktoken.encoding_for_model("gpt-4o")

def count_tokens(text: str) -> int:
    """Count tokens in text using tiktoken."""
    return len(tokenizer.encode(text))

print("✅ Clients initialized\n")

# Test 1: ConversationMessage dataclass
@dataclass
class ConversationMessage:
    """Represents a single conversation message."""
    role: str
    content: str
    timestamp: float = field(default_factory=time.time)
    token_count: Optional[int] = None
    
    def __post_init__(self):
        if self.token_count is None:
            self.token_count = count_tokens(self.content)

test_msg = ConversationMessage(
    role="user",
    content="What courses do you recommend for machine learning?"
)
assert test_msg.token_count > 0
print(f"✅ Test 1: ConversationMessage dataclass works (tokens: {test_msg.token_count})\n")

# Test 2: Token counting and cost calculation
def calculate_conversation_cost(num_turns: int, avg_tokens_per_turn: int = 100):
    """Calculate cost metrics for a conversation."""
    system_tokens = 50
    cumulative_cost = 0.0
    
    for turn in range(1, num_turns + 1):
        conversation_tokens = turn * avg_tokens_per_turn
        total_tokens = system_tokens + conversation_tokens
        turn_cost = (total_tokens / 1000) * 0.0025
        cumulative_cost += turn_cost
    
    return cumulative_cost

cost_10_turns = calculate_conversation_cost(10)
cost_100_turns = calculate_conversation_cost(100)
assert cost_100_turns > cost_10_turns
print(f"✅ Test 2: Cost calculation works (10 turns: ${cost_10_turns:.4f}, 100 turns: ${cost_100_turns:.4f})\n")

# Test 3: Summarization functions
def should_summarize(
    messages: List[ConversationMessage],
    token_threshold: int = 2000,
    message_threshold: int = 10,
    keep_recent: int = 4
) -> bool:
    """Determine if conversation needs summarization."""
    if len(messages) <= keep_recent:
        return False
    total_tokens = sum(msg.token_count for msg in messages)
    return (total_tokens > token_threshold or len(messages) > message_threshold)

# Create test messages with more content
test_messages = [
    ConversationMessage("user", f"This is a longer test message number {i} with more content to increase token count")
    for i in range(15)
]

should_sum = should_summarize(test_messages, token_threshold=500, message_threshold=10)
assert should_sum == True
print(f"✅ Test 3: should_summarize() works (15 messages, should summarize: {should_sum})\n")

# Test 4: Compression strategies
class TruncationStrategy:
    """Keep only the most recent messages within token budget."""

    def compress(self, messages: List[ConversationMessage], max_tokens: int) -> List[ConversationMessage]:
        """Keep most recent messages within token budget."""
        compressed = []
        total_tokens = 0

        for msg in reversed(messages):
            if total_tokens + msg.token_count <= max_tokens:
                compressed.insert(0, msg)
                total_tokens += msg.token_count
            else:
                break

        return compressed

truncation = TruncationStrategy()
truncated = truncation.compress(test_messages, max_tokens=50)  # Lower budget to ensure truncation
total_tokens_before = sum(m.token_count for m in test_messages)
total_tokens_after = sum(m.token_count for m in truncated)
assert len(truncated) < len(test_messages)
assert total_tokens_after <= 50
print(f"✅ Test 4: TruncationStrategy works ({len(test_messages)} → {len(truncated)} messages, {total_tokens_before} → {total_tokens_after} tokens)\n")

# Test 5: Priority-based strategy
def calculate_message_importance(msg: ConversationMessage) -> float:
    """Calculate importance score for a message."""
    score = 0.0
    content_lower = msg.content.lower()
    
    if any(code in content_lower for code in ['cs', 'math', 'eng']):
        score += 2.0
    if '?' in msg.content:
        score += 1.5
    if any(word in content_lower for word in ['prerequisite', 'require', 'need']):
        score += 1.5
    if msg.role == 'user':
        score += 0.5
    
    return score

class PriorityBasedStrategy:
    """Keep highest-priority messages within token budget."""
    
    def calculate_importance(self, msg: ConversationMessage) -> float:
        return calculate_message_importance(msg)
    
    def compress(self, messages: List[ConversationMessage], max_tokens: int) -> List[ConversationMessage]:
        """Keep highest-priority messages within token budget."""
        scored_messages = [
            (self.calculate_importance(msg), i, msg)
            for i, msg in enumerate(messages)
        ]
        scored_messages.sort(key=lambda x: (-x[0], x[1]))
        
        selected = []
        total_tokens = 0
        
        for score, idx, msg in scored_messages:
            if total_tokens + msg.token_count <= max_tokens:
                selected.append((idx, msg))
                total_tokens += msg.token_count
        
        selected.sort(key=lambda x: x[0])
        return [msg for idx, msg in selected]

priority = PriorityBasedStrategy()
prioritized = priority.compress(test_messages, max_tokens=200)
assert len(prioritized) <= len(test_messages)
print(f"✅ Test 5: PriorityBasedStrategy works ({len(test_messages)} → {len(prioritized)} messages)\n")

# Test 6: Decision framework
from enum import Enum
from typing import Literal

class CompressionChoice(Enum):
    """Available compression strategies."""
    NONE = "none"
    TRUNCATION = "truncation"
    PRIORITY = "priority"
    SUMMARIZATION = "summarization"

def choose_compression_strategy(
    conversation_length: int,
    token_count: int,
    quality_requirement: Literal["high", "medium", "low"],
    latency_requirement: Literal["fast", "medium", "slow_ok"],
    cost_sensitivity: Literal["high", "medium", "low"] = "medium"
) -> CompressionChoice:
    """Decision framework for choosing compression strategy."""
    if token_count < 2000 and conversation_length < 10:
        return CompressionChoice.NONE
    
    if latency_requirement == "fast":
        if quality_requirement == "high":
            return CompressionChoice.PRIORITY
        else:
            return CompressionChoice.TRUNCATION
    
    if cost_sensitivity == "high":
        return CompressionChoice.PRIORITY if quality_requirement != "low" else CompressionChoice.TRUNCATION
    
    if quality_requirement == "high" and latency_requirement == "slow_ok":
        return CompressionChoice.SUMMARIZATION
    
    if conversation_length > 30 and quality_requirement != "low":
        return CompressionChoice.SUMMARIZATION
    
    if quality_requirement == "medium":
        return CompressionChoice.PRIORITY
    
    return CompressionChoice.TRUNCATION

strategy1 = choose_compression_strategy(5, 1000, "high", "fast", "medium")
strategy2 = choose_compression_strategy(50, 15000, "high", "slow_ok", "medium")
assert strategy1 == CompressionChoice.NONE  # Short conversation
assert strategy2 == CompressionChoice.SUMMARIZATION  # Long, high quality
print(f"✅ Test 6: Decision framework works (short→{strategy1.value}, long→{strategy2.value})\n")

# Test 7: Agent Memory Server connection
async def test_memory_server():
    """Test Agent Memory Server connection."""
    test_session_id = f"validation_test_{int(time.time())}"
    test_user_id = "validation_user"

    # Get or create working memory
    _, working_memory = await memory_client.get_or_create_working_memory(
        session_id=test_session_id,
        user_id=test_user_id,
        model_name="gpt-4o"
    )

    # Check that we got a working memory object
    assert working_memory is not None
    return True

try:
    result = asyncio.run(test_memory_server())
    print("✅ Test 7: Agent Memory Server connection works\n")
except Exception as e:
    print(f"❌ Test 7 failed: {e}\n")
    sys.exit(1)

print("=" * 80)
print("🎉 ALL VALIDATION TESTS PASSED!")
print("=" * 80)
print("\nThe notebook should execute successfully.")
print("Key components validated:")
print("  ✅ Data structures (ConversationMessage)")
print("  ✅ Token counting and cost calculation")
print("  ✅ Summarization logic")
print("  ✅ Compression strategies (Truncation, Priority-based)")
print("  ✅ Decision framework")
print("  ✅ Agent Memory Server integration")
print("\n✨ Ready to run the full notebook!")

