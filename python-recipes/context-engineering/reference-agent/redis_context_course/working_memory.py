"""
Working memory system with long-term extraction strategies.

This module implements working memory that temporarily holds conversation context
and applies configurable strategies for extracting important information to long-term memory.
"""

import json
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Set
from enum import Enum
from dataclasses import dataclass

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_core.tools import tool
from pydantic import BaseModel, Field

from .models import ConversationMemory
from .redis_config import redis_config


class ExtractionTrigger(str, Enum):
    """When to trigger long-term memory extraction."""
    MESSAGE_COUNT = "message_count"  # After N messages
    TIME_BASED = "time_based"       # After time interval
    IMPORTANCE_THRESHOLD = "importance_threshold"  # When importance exceeds threshold
    MANUAL = "manual"               # Only when explicitly called
    CONVERSATION_END = "conversation_end"  # At end of conversation


@dataclass
class WorkingMemoryItem:
    """Item stored in working memory."""
    content: str
    message_type: str  # "human", "ai", "system"
    timestamp: datetime
    importance: float = 0.5
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class LongTermExtractionStrategy(ABC):
    """Abstract base class for long-term memory extraction strategies."""
    
    def __init__(self, name: str, config: Dict[str, Any] = None):
        self.name = name
        self.config = config or {}
    
    @abstractmethod
    def should_extract(self, working_memory: 'WorkingMemory') -> bool:
        """Determine if extraction should happen now."""
        pass
    
    @abstractmethod
    def extract_memories(self, working_memory: 'WorkingMemory') -> List[ConversationMemory]:
        """Extract memories from working memory for long-term storage."""
        pass
    
    @abstractmethod
    def calculate_importance(self, content: str, context: Dict[str, Any]) -> float:
        """Calculate importance score for a piece of content."""
        pass
    
    @property
    def trigger_condition(self) -> str:
        """Human-readable description of when extraction triggers."""
        return "Custom extraction logic"
    
    @property
    def priority_criteria(self) -> str:
        """Human-readable description of what gets prioritized."""
        return "Custom priority logic"


class MessageCountStrategy(LongTermExtractionStrategy):
    """Extract memories after a certain number of messages."""
    
    def __init__(self, message_threshold: int = 10, min_importance: float = 0.6):
        super().__init__("message_count", {
            "message_threshold": message_threshold,
            "min_importance": min_importance
        })
        self.message_threshold = message_threshold
        self.min_importance = min_importance
    
    def should_extract(self, working_memory: 'WorkingMemory') -> bool:
        return len(working_memory.items) >= self.message_threshold
    
    def extract_memories(self, working_memory: 'WorkingMemory') -> List[ConversationMemory]:
        """Extract high-importance items and conversation summaries."""
        memories = []
        
        # Extract high-importance individual items
        for item in working_memory.items:
            if item.importance >= self.min_importance:
                memory = ConversationMemory(
                    student_id=working_memory.student_id,
                    content=item.content,
                    memory_type=self._determine_memory_type(item),
                    importance=item.importance,
                    metadata={
                        **item.metadata,
                        "extracted_from": "working_memory",
                        "extraction_strategy": self.name,
                        "original_timestamp": item.timestamp.isoformat()
                    }
                )
                memories.append(memory)
        
        # Create conversation summary
        if len(working_memory.items) > 3:
            summary_content = self._create_conversation_summary(working_memory.items)
            summary_memory = ConversationMemory(
                student_id=working_memory.student_id,
                content=summary_content,
                memory_type="conversation_summary",
                importance=0.8,
                metadata={
                    "message_count": len(working_memory.items),
                    "extraction_strategy": self.name,
                    "summary_created": datetime.now().isoformat()
                }
            )
            memories.append(summary_memory)
        
        return memories
    
    def calculate_importance(self, content: str, context: Dict[str, Any]) -> float:
        """Calculate importance based on content analysis."""
        importance = 0.5  # Base importance
        
        # Boost importance for certain keywords
        high_importance_keywords = ["prefer", "goal", "want", "need", "important", "hate", "love"]
        medium_importance_keywords = ["like", "interested", "consider", "maybe", "think"]
        
        content_lower = content.lower()
        for keyword in high_importance_keywords:
            if keyword in content_lower:
                importance += 0.2
        
        for keyword in medium_importance_keywords:
            if keyword in content_lower:
                importance += 0.1
        
        # Boost for questions (likely important for understanding student needs)
        if "?" in content:
            importance += 0.1
        
        # Boost for personal statements
        if any(pronoun in content_lower for pronoun in ["i ", "my ", "me ", "myself"]):
            importance += 0.1
        
        return min(importance, 1.0)
    
    def _determine_memory_type(self, item: WorkingMemoryItem) -> str:
        """Determine the type of memory based on content."""
        content_lower = item.content.lower()
        
        if any(word in content_lower for word in ["prefer", "like", "hate", "love"]):
            return "preference"
        elif any(word in content_lower for word in ["goal", "want", "plan", "aim"]):
            return "goal"
        elif any(word in content_lower for word in ["experience", "did", "was", "went"]):
            return "experience"
        else:
            return "general"
    
    def _create_conversation_summary(self, items: List[WorkingMemoryItem]) -> str:
        """Create a summary of the conversation."""
        human_messages = [item for item in items if item.message_type == "human"]
        ai_messages = [item for item in items if item.message_type == "ai"]
        
        summary = f"Conversation summary ({len(items)} messages): "
        
        if human_messages:
            # Extract key topics from human messages
            topics = set()
            for msg in human_messages:
                # Simple topic extraction (could be enhanced with NLP)
                words = msg.content.lower().split()
                for word in words:
                    if len(word) > 4 and word not in ["that", "this", "with", "have", "been"]:
                        topics.add(word)
            
            if topics:
                summary += f"Student discussed: {', '.join(list(topics)[:5])}. "
        
        summary += f"Agent provided {len(ai_messages)} responses with course recommendations and guidance."
        
        return summary
    
    @property
    def trigger_condition(self) -> str:
        return f"After {self.message_threshold} messages"
    
    @property
    def priority_criteria(self) -> str:
        return f"Items with importance >= {self.min_importance}, plus conversation summary"


class WorkingMemory:
    """Working memory that holds temporary conversation context."""
    
    def __init__(self, student_id: str, extraction_strategy: LongTermExtractionStrategy = None):
        self.student_id = student_id
        self.items: List[WorkingMemoryItem] = []
        self.created_at = datetime.now()
        self.last_extraction = None
        self.extraction_strategy = extraction_strategy or MessageCountStrategy()
        
        # Redis key for persistence
        self.redis_key = f"working_memory:{student_id}"
        self.redis_client = redis_config.redis_client
        
        # Load existing working memory if available
        self._load_from_redis()
    
    def add_message(self, message: BaseMessage, importance: float = None) -> None:
        """Add a message to working memory."""
        if isinstance(message, HumanMessage):
            message_type = "human"
        elif isinstance(message, AIMessage):
            message_type = "ai"
        else:
            message_type = "system"
        
        # Calculate importance if not provided
        if importance is None:
            context = {"message_type": message_type, "current_items": len(self.items)}
            importance = self.extraction_strategy.calculate_importance(message.content, context)
        
        item = WorkingMemoryItem(
            content=message.content,
            message_type=message_type,
            timestamp=datetime.now(),
            importance=importance,
            metadata={"message_id": getattr(message, 'id', None)}
        )
        
        self.items.append(item)
        self._save_to_redis()
    
    def add_memories(self, memories: List[str], memory_type: str = "general") -> None:
        """Add multiple memories to working memory."""
        for memory in memories:
            context = {"memory_type": memory_type, "current_items": len(self.items)}
            importance = self.extraction_strategy.calculate_importance(memory, context)
            
            item = WorkingMemoryItem(
                content=memory,
                message_type="memory",
                timestamp=datetime.now(),
                importance=importance,
                metadata={"memory_type": memory_type}
            )
            
            self.items.append(item)
        
        self._save_to_redis()
    
    def should_extract_to_long_term(self) -> bool:
        """Check if extraction should happen based on strategy."""
        return self.extraction_strategy.should_extract(self)
    
    def extract_to_long_term(self) -> List[ConversationMemory]:
        """Extract memories for long-term storage."""
        memories = self.extraction_strategy.extract_memories(self)
        self.last_extraction = datetime.now()
        
        # Clear extracted items (keep recent ones)
        self._cleanup_after_extraction()
        self._save_to_redis()
        
        return memories
    
    def get_current_context(self, limit: int = 10) -> List[WorkingMemoryItem]:
        """Get recent items for context."""
        return self.items[-limit:] if len(self.items) > limit else self.items
    
    def clear(self) -> None:
        """Clear working memory."""
        self.items = []
        self.redis_client.delete(self.redis_key)
    
    def _cleanup_after_extraction(self) -> None:
        """Keep only the most recent items after extraction."""
        # Keep last 5 items to maintain conversation continuity
        if len(self.items) > 5:
            self.items = self.items[-5:]
    
    def _save_to_redis(self) -> None:
        """Save working memory to Redis."""
        data = {
            "student_id": self.student_id,
            "created_at": self.created_at.isoformat(),
            "last_extraction": self.last_extraction.isoformat() if self.last_extraction else None,
            "extraction_strategy": {
                "name": self.extraction_strategy.name,
                "config": self.extraction_strategy.config
            },
            "items": [
                {
                    "content": item.content,
                    "message_type": item.message_type,
                    "timestamp": item.timestamp.isoformat(),
                    "importance": item.importance,
                    "metadata": item.metadata
                }
                for item in self.items
            ]
        }
        
        # Set TTL to 24 hours
        self.redis_client.setex(self.redis_key, 86400, json.dumps(data))
    
    def _load_from_redis(self) -> None:
        """Load working memory from Redis."""
        data = self.redis_client.get(self.redis_key)
        if data:
            try:
                parsed_data = json.loads(data)
                self.created_at = datetime.fromisoformat(parsed_data["created_at"])
                if parsed_data.get("last_extraction"):
                    self.last_extraction = datetime.fromisoformat(parsed_data["last_extraction"])
                
                # Restore items
                self.items = []
                for item_data in parsed_data.get("items", []):
                    item = WorkingMemoryItem(
                        content=item_data["content"],
                        message_type=item_data["message_type"],
                        timestamp=datetime.fromisoformat(item_data["timestamp"]),
                        importance=item_data["importance"],
                        metadata=item_data.get("metadata", {})
                    )
                    self.items.append(item)
                    
            except (json.JSONDecodeError, KeyError, ValueError) as e:
                # If loading fails, start fresh
                self.items = []
                self.created_at = datetime.now()
                self.last_extraction = None
