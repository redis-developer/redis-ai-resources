"""
Memory client wrapper for Redis Agent Memory Server.

This module provides a simplified interface to the Agent Memory Server,
which handles both working memory (task-focused context) and long-term memory
(cross-session knowledge).
"""

import os
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime

from agent_memory_client import MemoryAPIClient, MemoryClientConfig
from agent_memory_client.models import (
    MemoryRecord,
    MemoryMessage,
    WorkingMemory
)


class MemoryClient:
    """
    Simplified client for Redis Agent Memory Server.
    
    Provides easy access to:
    - Working memory: Session-scoped, task-focused context
    - Long-term memory: Cross-session, persistent knowledge
    """
    
    def __init__(
        self,
        user_id: str,
        namespace: str = "redis_university",
        base_url: Optional[str] = None
    ):
        """
        Initialize memory client.
        
        Args:
            user_id: Unique identifier for the user/student
            namespace: Namespace for memory isolation (default: redis_university)
            base_url: Agent Memory Server URL (default: from env or localhost:8000)
        """
        self.user_id = user_id
        self.namespace = namespace

        # Get base URL from environment or use default
        if base_url is None:
            base_url = os.getenv("AGENT_MEMORY_URL", "http://localhost:8000")

        # Create config and client
        config = MemoryClientConfig(base_url=base_url, default_namespace=namespace)
        self.client = MemoryAPIClient(config=config)
    
    # ==================== Working Memory ====================
    
    async def get_working_memory(
        self,
        session_id: str,
        model_name: str = "gpt-4o"
    ) -> Optional[WorkingMemory]:
        """
        Get working memory for a session.

        Working memory contains:
        - Conversation messages
        - Structured memories awaiting promotion
        - Session-specific data

        Args:
            session_id: Session identifier
            model_name: Model name for context window management

        Returns:
            WorkingMemory object or None if not found
        """
        return await self.client.get_working_memory(
            session_id=session_id,
            namespace=self.namespace,
            model_name=model_name
        )

    async def get_or_create_working_memory(
        self,
        session_id: str,
        model_name: str = "gpt-4o"
    ) -> WorkingMemory:
        """
        Get or create working memory for a session.

        This method will create a new working memory if one doesn't exist,
        making it safe to use at the start of a session.

        Args:
            session_id: Session identifier
            model_name: Model name for context window management

        Returns:
            WorkingMemory object (existing or newly created)
        """
        # The client returns a tuple (WorkingMemory, bool) where bool indicates if it was created
        working_memory, _ = await self.client.get_or_create_working_memory(
            session_id=session_id,
            user_id=self.user_id,
            namespace=self.namespace,
            model_name=model_name
        )
        return working_memory

    async def save_working_memory(
        self,
        session_id: str,
        messages: Optional[List[Dict[str, str]]] = None,
        memories: Optional[List[Dict[str, Any]]] = None,
        data: Optional[Dict[str, Any]] = None,
        model_name: str = "gpt-4o"
    ) -> WorkingMemory:
        """
        Save working memory for a session.
        
        Args:
            session_id: Session identifier
            messages: Conversation messages (role/content pairs)
            memories: Structured memories to promote to long-term storage
            data: Arbitrary session data (stays in working memory only)
            model_name: Model name for context window management
            
        Returns:
            Updated WorkingMemory object
        """
        # Convert messages to MemoryMessage objects
        memory_messages = []
        if messages:
            for msg in messages:
                memory_messages.append(
                    MemoryMessage(
                        role=msg.get("role", "user"),
                        content=msg.get("content", "")
                    )
                )
        
        # Convert memories to MemoryRecord objects
        memory_records = []
        if memories:
            for mem in memories:
                memory_records.append(
                    MemoryRecord(
                        id=str(uuid.uuid4()),
                        text=mem.get("text", ""),
                        session_id=session_id,
                        user_id=self.user_id,
                        namespace=self.namespace,
                        memory_type=mem.get("memory_type", "semantic"),
                        topics=mem.get("topics", []),
                        entities=mem.get("entities", []),
                        event_date=mem.get("event_date")
                    )
                )
        
        working_memory = WorkingMemory(
            session_id=session_id,
            user_id=self.user_id,
            namespace=self.namespace,
            messages=memory_messages,
            memories=memory_records,
            data=data or {},
            model_name=model_name
        )

        return await self.client.put_working_memory(
            session_id=session_id,
            memory=working_memory,
            user_id=self.user_id,
            model_name=model_name
        )
    
    async def add_message_to_working_memory(
        self,
        session_id: str,
        role: str,
        content: str,
        model_name: str = "gpt-4o"
    ) -> WorkingMemory:
        """
        Add a single message to working memory.
        
        Args:
            session_id: Session identifier
            role: Message role (user, assistant, system)
            content: Message content
            model_name: Model name for context window management
            
        Returns:
            Updated WorkingMemory object
        """
        # Get existing working memory
        wm = await self.get_working_memory(session_id, model_name)
        
        messages = []
        if wm and wm.messages:
            messages = [{"role": m.role, "content": m.content} for m in wm.messages]
        
        messages.append({"role": role, "content": content})
        
        return await self.save_working_memory(
            session_id=session_id,
            messages=messages,
            model_name=model_name
        )
    
    # ==================== Long-term Memory ====================
    
    async def create_memory(
        self,
        text: str,
        memory_type: str = "semantic",
        topics: Optional[List[str]] = None,
        entities: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        event_date: Optional[datetime] = None
    ) -> List[MemoryRecord]:
        """
        Create a long-term memory directly.
        
        Long-term memories are persistent across all sessions and
        searchable via semantic vector search.
        
        Args:
            text: Memory content
            memory_type: Type of memory (semantic, episodic, message)
            topics: Related topics for filtering
            entities: Named entities mentioned
            metadata: Additional metadata
            event_date: For episodic memories, when the event occurred
            
        Returns:
            List of created MemoryRecord objects
        """
        memory = MemoryRecord(
            id=str(uuid.uuid4()),
            text=text,
            user_id=self.user_id,
            namespace=self.namespace,
            memory_type=memory_type,
            topics=topics or [],
            entities=entities or [],
            event_date=event_date
        )

        # The client may return a tuple (memories, metadata) or just memories
        result = await self.client.create_long_term_memories([memory])
        # If it's a tuple, unpack it; otherwise return as-is
        if isinstance(result, tuple):
            memories, _ = result
            return memories
        return result
    
    async def search_memories(
        self,
        query: str,
        limit: int = 10,
        memory_types: Optional[List[str]] = None,
        topics: Optional[List[str]] = None,
        distance_threshold: float = 0.8
    ) -> List[MemoryRecord]:
        """
        Search long-term memories using semantic search.

        Args:
            query: Search query text
            limit: Maximum number of results
            memory_types: Filter by memory types (semantic, episodic, message)
            topics: Filter by topics
            distance_threshold: Minimum similarity score (0.0-1.0)

        Returns:
            List of matching MemoryRecord objects
        """
        # Build filters dict (simplified API)
        filters = {
            "user_id": self.user_id,
            "namespace": self.namespace
        }

        if memory_types:
            filters["memory_type"] = memory_types

        if topics:
            filters["topics"] = topics

        try:
            results = await self.client.search_long_term_memory(
                text=query,
                filters=filters,
                limit=limit,
                distance_threshold=distance_threshold
            )

            return results.memories if results else []
        except Exception as e:
            # If search fails, return empty list (graceful degradation)
            print(f"Warning: Memory search failed: {e}")
            return []
    
    async def get_memory_prompt(
        self,
        session_id: str,
        query: str,
        model_name: str = "gpt-4o",
        context_window_max: int = 4000,
        search_limit: int = 5
    ) -> List[Dict[str, str]]:
        """
        Get a memory-enriched prompt ready for the LLM.
        
        This combines:
        - Working memory (conversation context)
        - Relevant long-term memories (semantic search)
        - Current query
        
        Args:
            session_id: Session identifier
            query: User's current query
            model_name: Model name for context window management
            context_window_max: Maximum context window size
            search_limit: Number of long-term memories to retrieve
            
        Returns:
            List of messages ready for LLM
        """
        response = await self.client.memory_prompt(
            query=query,
            session={
                "session_id": session_id,
                "user_id": self.user_id,
                "namespace": self.namespace,
                "model_name": model_name,
                "context_window_max": context_window_max
            },
            long_term_search={
                "text": query,
                "filters": {
                    "user_id": {"eq": self.user_id},
                    "namespace": {"eq": self.namespace}
                },
                "limit": search_limit
            }
        )
        
        return response.messages if response else []

