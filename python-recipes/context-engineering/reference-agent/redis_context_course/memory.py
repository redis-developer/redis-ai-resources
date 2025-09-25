"""
Memory management system for the Class Agent.

This module handles both short-term (conversation) and long-term (persistent) memory
using Redis and vector storage for semantic retrieval.
"""

import json
from datetime import datetime
from typing import List, Optional, Dict, Any
import numpy as np

# Conditional imports for RedisVL - may not be available in all environments
try:
    from redisvl.query import VectorQuery
    from redisvl.query.filter import Tag
    REDISVL_AVAILABLE = True
except ImportError:
    # Fallback for environments without RedisVL
    VectorQuery = None
    Tag = None
    REDISVL_AVAILABLE = False

try:
    from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
except ImportError:
    # Fallback for environments without LangChain
    BaseMessage = None
    HumanMessage = None
    AIMessage = None

from .models import ConversationMemory, StudentProfile
from .redis_config import redis_config


class MemoryManager:
    """Manages both short-term and long-term memory for the agent."""

    def __init__(self, student_id: str):
        self.student_id = student_id
        self.redis_client = redis_config.redis_client
        self.memory_index = redis_config.memory_index
        self.embeddings = redis_config.embeddings

    def _build_memory_filters(self, memory_types: Optional[List[str]] = None):
        """
        Build filter expressions for memory queries.

        Uses RedisVL filter classes if available, otherwise falls back to string construction.
        This provides compatibility across different environments.
        """
        if REDISVL_AVAILABLE and Tag is not None:
            # Use RedisVL filter classes (preferred approach)
            filter_conditions = [Tag("student_id") == self.student_id]

            if memory_types:
                if len(memory_types) == 1:
                    filter_conditions.append(Tag("memory_type") == memory_types[0])
                else:
                    # Create OR condition for multiple memory types
                    memory_type_filter = Tag("memory_type") == memory_types[0]
                    for memory_type in memory_types[1:]:
                        memory_type_filter = memory_type_filter | (Tag("memory_type") == memory_type)
                    filter_conditions.append(memory_type_filter)

            # Combine all filters with AND logic
            combined_filter = filter_conditions[0]
            for condition in filter_conditions[1:]:
                combined_filter = combined_filter & condition

            return combined_filter

        # Fallback to string-based filter construction
        filters = [f"@student_id:{{{self.student_id}}}"]
        if memory_types:
            type_filter = "|".join(memory_types)
            filters.append(f"@memory_type:{{{type_filter}}}")

        return " ".join(filters)
    
    async def store_memory(
        self,
        content: str,
        memory_type: str = "general",
        importance: float = 1.0,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Store a memory in long-term storage with vector embedding."""
        memory = ConversationMemory(
            student_id=self.student_id,
            content=content,
            memory_type=memory_type,
            importance=importance,
            metadata=metadata or {}
        )
        
        # Generate embedding for semantic search
        embedding = await self.embeddings.aembed_query(content)
        
        # Store in Redis with vector
        memory_data = {
            "id": memory.id,
            "student_id": memory.student_id,
            "content": memory.content,
            "memory_type": memory.memory_type,
            "importance": memory.importance,
            "created_at": memory.created_at.timestamp(),
            "metadata": json.dumps(memory.metadata),
            "content_vector": np.array(embedding, dtype=np.float32).tobytes()
        }
        
        key = f"{redis_config.memory_index_name}:{memory.id}"
        self.redis_client.hset(key, mapping=memory_data)
        
        return memory.id
    
    async def retrieve_memories(
        self,
        query: str,
        memory_types: Optional[List[str]] = None,
        limit: int = 5,
        similarity_threshold: float = 0.7
    ) -> List[ConversationMemory]:
        """Retrieve relevant memories using semantic search."""
        # Generate query embedding
        query_embedding = await self.embeddings.aembed_query(query)
        
        # Build vector query
        vector_query = VectorQuery(
            vector=query_embedding,
            vector_field_name="content_vector",
            return_fields=["id", "student_id", "content", "memory_type", "importance", "created_at", "metadata"],
            num_results=limit
        )
        
        # Add filters using the helper method
        filter_expression = self._build_memory_filters(memory_types)
        vector_query.set_filter(filter_expression)
        
        # Execute search
        results = self.memory_index.query(vector_query)
        
        # Convert results to ConversationMemory objects
        memories = []
        for result in results.docs:
            if result.vector_score >= similarity_threshold:
                memory = ConversationMemory(
                    id=result.id,
                    student_id=result.student_id,
                    content=result.content,
                    memory_type=result.memory_type,
                    importance=float(result.importance),
                    created_at=datetime.fromtimestamp(float(result.created_at)),
                    metadata=json.loads(result.metadata) if result.metadata else {}
                )
                memories.append(memory)
        
        return memories
    
    def get_conversation_summary(self, messages: List[BaseMessage], max_length: int = 500) -> str:
        """Generate a summary of recent conversation for context management."""
        if not messages:
            return ""
        
        # Extract key information from recent messages
        recent_messages = messages[-10:]  # Last 10 messages
        
        summary_parts = []
        for msg in recent_messages:
            if isinstance(msg, HumanMessage):
                summary_parts.append(f"Student: {msg.content[:100]}...")
            elif isinstance(msg, AIMessage):
                summary_parts.append(f"Agent: {msg.content[:100]}...")
        
        summary = " | ".join(summary_parts)
        
        # Truncate if too long
        if len(summary) > max_length:
            summary = summary[:max_length] + "..."
        
        return summary
    
    async def store_conversation_summary(self, messages: List[BaseMessage]) -> str:
        """Store a conversation summary as a memory."""
        summary = self.get_conversation_summary(messages)
        if summary:
            return await self.store_memory(
                content=summary,
                memory_type="conversation_summary",
                importance=0.8,
                metadata={"message_count": len(messages)}
            )
        return ""
    
    async def store_preference(self, preference: str, context: str = "") -> str:
        """Store a student preference."""
        content = f"Student preference: {preference}"
        if context:
            content += f" (Context: {context})"
        
        return await self.store_memory(
            content=content,
            memory_type="preference",
            importance=0.9,
            metadata={"preference": preference, "context": context}
        )
    
    async def store_goal(self, goal: str, context: str = "") -> str:
        """Store a student goal or objective."""
        content = f"Student goal: {goal}"
        if context:
            content += f" (Context: {context})"
        
        return await self.store_memory(
            content=content,
            memory_type="goal",
            importance=1.0,
            metadata={"goal": goal, "context": context}
        )
    
    async def get_student_context(self, query: str = "") -> Dict[str, Any]:
        """Get comprehensive student context for the agent."""
        context = {
            "preferences": [],
            "goals": [],
            "recent_conversations": [],
            "general_memories": []
        }
        
        # Retrieve different types of memories
        if query:
            # Get relevant memories for the current query
            relevant_memories = await self.retrieve_memories(query, limit=10)
            for memory in relevant_memories:
                if memory.memory_type == "preference":
                    context["preferences"].append(memory.content)
                elif memory.memory_type == "goal":
                    context["goals"].append(memory.content)
                elif memory.memory_type == "conversation_summary":
                    context["recent_conversations"].append(memory.content)
                else:
                    context["general_memories"].append(memory.content)
        else:
            # Get recent memories of each type
            for memory_type in ["preference", "goal", "conversation_summary", "general"]:
                memories = await self.retrieve_memories(
                    query="recent interactions",
                    memory_types=[memory_type],
                    limit=3
                )
                context[f"{memory_type}s"] = [m.content for m in memories]
        
        return context
