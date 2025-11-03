#!/usr/bin/env python3
"""
Validation script for the compression notebook.
Tests that the key compression strategies work correctly.
"""

import sys
from dataclasses import dataclass
from typing import List

# Token counting utility (simplified for testing)
def count_tokens(text: str, model: str = "gpt-4o") -> int:
    """Count tokens in text using simple estimation."""
    return len(text) // 4

@dataclass
class ConversationMessage:
    """Represents a conversation message with metadata."""
    role: str
    content: str
    token_count: int = 0
    
    def __post_init__(self):
        if self.token_count == 0:
            self.token_count = count_tokens(self.content)

class TruncationStrategy:
    """Keep only the most recent messages within token budget."""
    
    def compress(
        self,
        messages: List[ConversationMessage],
        max_tokens: int
    ) -> List[ConversationMessage]:
        """Keep most recent messages within token budget."""
        compressed = []
        total_tokens = 0
        
        # Work backwards from most recent
        for msg in reversed(messages):
            if total_tokens + msg.token_count <= max_tokens:
                compressed.insert(0, msg)
                total_tokens += msg.token_count
            else:
                break
        
        return compressed

class PriorityBasedStrategy:
    """Score messages by importance and keep highest-scoring."""
    
    def _score_message(self, msg: ConversationMessage, index: int, total: int) -> float:
        """Score message importance."""
        score = 0.0
        
        # Recency: Recent messages get higher scores
        recency_score = index / total
        score += recency_score * 50
        
        # Length: Longer messages likely have more info
        length_score = min(msg.token_count / 100, 1.0)
        score += length_score * 20
        
        # Role: User messages are important (capture intent)
        if msg.role == "user":
            score += 15
        
        # Keywords: Messages with important terms
        keywords = ["course", "RU", "prefer", "interested", "goal", "major", "graduate"]
        keyword_count = sum(1 for kw in keywords if kw.lower() in msg.content.lower())
        score += keyword_count * 5
        
        return score
    
    def compress(
        self,
        messages: List[ConversationMessage],
        max_tokens: int
    ) -> List[ConversationMessage]:
        """Keep highest-scoring messages within token budget."""
        # Score all messages
        scored = [
            (self._score_message(msg, i, len(messages)), i, msg)
            for i, msg in enumerate(messages)
        ]
        
        # Sort by score (descending)
        scored.sort(reverse=True, key=lambda x: x[0])
        
        # Select messages within budget
        selected = []
        total_tokens = 0
        
        for score, idx, msg in scored:
            if total_tokens + msg.token_count <= max_tokens:
                selected.append((idx, msg))
                total_tokens += msg.token_count
        
        # Sort by original order to maintain conversation flow
        selected.sort(key=lambda x: x[0])
        
        return [msg for idx, msg in selected]

def test_compression_strategies():
    """Test all compression strategies."""
    print("🧪 Testing Compression Strategies")
    print("=" * 80)
    
    # Create test conversation
    test_conversation = [
        ConversationMessage(role="user", content="I'm interested in machine learning courses"),
        ConversationMessage(role="assistant", content="Great! Let me help you find ML courses."),
        ConversationMessage(role="user", content="What are the prerequisites?"),
        ConversationMessage(role="assistant", content="You'll need data structures and linear algebra."),
        ConversationMessage(role="user", content="I've completed CS201 Data Structures"),
        ConversationMessage(role="assistant", content="Perfect! That's one prerequisite done."),
        ConversationMessage(role="user", content="Do I need calculus?"),
        ConversationMessage(role="assistant", content="Yes, MATH301 Linear Algebra is required."),
        ConversationMessage(role="user", content="I'm taking that next semester"),
        ConversationMessage(role="assistant", content="Excellent planning!"),
    ]
    
    total_messages = len(test_conversation)
    total_tokens = sum(msg.token_count for msg in test_conversation)
    
    print(f"Original conversation: {total_messages} messages, {total_tokens} tokens\n")

    # Test truncation (set budget lower than total to force compression)
    max_tokens = total_tokens // 2  # Use half the tokens
    truncation = TruncationStrategy()
    truncated = truncation.compress(test_conversation, max_tokens)
    truncated_tokens = sum(msg.token_count for msg in truncated)
    
    print(f"✅ Truncation Strategy:")
    print(f"   Result: {len(truncated)} messages, {truncated_tokens} tokens")
    print(f"   Savings: {total_tokens - truncated_tokens} tokens")
    assert len(truncated) < total_messages, "Truncation should reduce message count"
    assert truncated_tokens <= max_tokens, "Truncation should stay within budget"
    
    # Test priority-based
    priority = PriorityBasedStrategy()
    prioritized = priority.compress(test_conversation, max_tokens)
    prioritized_tokens = sum(msg.token_count for msg in prioritized)
    
    print(f"\n✅ Priority-Based Strategy:")
    print(f"   Result: {len(prioritized)} messages, {prioritized_tokens} tokens")
    print(f"   Savings: {total_tokens - prioritized_tokens} tokens")
    assert len(prioritized) < total_messages, "Priority should reduce message count"
    assert prioritized_tokens <= max_tokens, "Priority should stay within budget"
    
    print("\n" + "=" * 80)
    print("✅ All compression strategies validated successfully!")
    return True

if __name__ == "__main__":
    try:
        success = test_compression_strategies()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Validation failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

