"""
Working memory tools that are aware of long-term extraction strategies.

These tools provide the LLM with context about the working memory's extraction strategy
and enable intelligent memory management decisions.
"""

from typing import List, Dict, Any, Optional
from langchain_core.tools import tool
from langchain_core.runnables import RunnableConfig

from .working_memory import WorkingMemory, MessageCountStrategy
from .memory import MemoryManager


class WorkingMemoryToolProvider:
    """Provides working memory tools with extraction strategy context."""
    
    def __init__(self, working_memory: WorkingMemory, memory_manager: MemoryManager):
        self.working_memory = working_memory
        self.memory_manager = memory_manager
    
    def get_memory_tool_schemas(self) -> List:
        """Get memory tools with working memory context injected."""
        strategy = self.working_memory.extraction_strategy
        
        # Build context description for tools
        strategy_context = f"""
WORKING MEMORY CONTEXT:
- Current extraction strategy: {strategy.name}
- Extraction trigger: {strategy.trigger_condition}
- Priority criteria: {strategy.priority_criteria}
- Current working memory size: {len(self.working_memory.items)} items
- Last extraction: {self.working_memory.last_extraction or 'Never'}
- Should extract now: {self.working_memory.should_extract_to_long_term()}

This context should inform your decisions about when and what to store in memory.
"""
        
        # Create strategy-aware tools
        @tool
        async def add_memories_to_working_memory(
            memories: List[str],
            memory_type: str = "general",
            config: Optional[RunnableConfig] = None
        ) -> str:
            f"""
            Add memories to working memory with extraction strategy awareness.
            
            Use this tool to add important information to working memory. The system
            will automatically extract memories to long-term storage based on the
            configured extraction strategy.
            
            {strategy_context}
            
            Args:
                memories: List of memory contents to add
                memory_type: Type of memory (general, preference, goal, experience)
            """
            # Add memories to working memory
            self.working_memory.add_memories(memories, memory_type)
            
            result = f"Added {len(memories)} memories to working memory."
            
            # Check if extraction should happen
            if self.working_memory.should_extract_to_long_term():
                extracted_memories = self.working_memory.extract_to_long_term()
                
                # Store extracted memories in long-term storage
                stored_count = 0
                for memory in extracted_memories:
                    try:
                        await self.memory_manager.store_memory(
                            content=memory.content,
                            memory_type=memory.memory_type,
                            importance=memory.importance,
                            metadata=memory.metadata
                        )
                        stored_count += 1
                    except Exception as e:
                        # Log error but continue
                        pass
                
                result += f" Extraction triggered: {stored_count} memories moved to long-term storage."
            
            return result
        
        @tool
        async def create_memory(
            content: str,
            memory_type: str = "general",
            importance: float = None,
            store_immediately: bool = False,
            config: Optional[RunnableConfig] = None
        ) -> str:
            f"""
            Create a memory with extraction strategy awareness.
            
            This tool creates a memory and decides whether to store it immediately in
            long-term storage or add it to working memory based on the extraction strategy.
            
            {strategy_context}
            
            Args:
                content: The memory content
                memory_type: Type of memory (preference, goal, experience, general)
                importance: Importance score (0.0-1.0), auto-calculated if not provided
                store_immediately: Force immediate long-term storage
            """
            # Calculate importance if not provided
            if importance is None:
                context = {"memory_type": memory_type, "working_memory_size": len(self.working_memory.items)}
                importance = self.working_memory.extraction_strategy.calculate_importance(content, context)
            
            if store_immediately or importance >= 0.8:
                # Store directly in long-term memory for high-importance items
                try:
                    memory_id = await self.memory_manager.store_memory(
                        content=content,
                        memory_type=memory_type,
                        importance=importance,
                        metadata={"created_via": "create_memory_tool", "immediate_storage": True}
                    )
                    return f"High-importance memory stored directly in long-term storage (importance: {importance:.2f})"
                except Exception as e:
                    return f"Error storing memory: {str(e)}"
            else:
                # Add to working memory
                self.working_memory.add_memories([content], memory_type)
                
                result = f"Memory added to working memory (importance: {importance:.2f})."
                
                # Check if extraction should happen
                if self.working_memory.should_extract_to_long_term():
                    extracted_memories = self.working_memory.extract_to_long_term()
                    
                    # Store extracted memories
                    stored_count = 0
                    for memory in extracted_memories:
                        try:
                            await self.memory_manager.store_memory(
                                content=memory.content,
                                memory_type=memory.memory_type,
                                importance=memory.importance,
                                metadata=memory.metadata
                            )
                            stored_count += 1
                        except Exception as e:
                            pass
                    
                    result += f" Extraction triggered: {stored_count} memories moved to long-term storage."
                
                return result
        
        @tool
        def get_working_memory_status(config: Optional[RunnableConfig] = None) -> str:
            f"""
            Get current working memory status and extraction strategy information.
            
            Use this tool to understand the current state of working memory and
            make informed decisions about memory management.
            
            {strategy_context}
            """
            status = f"""
WORKING MEMORY STATUS:
- Items in working memory: {len(self.working_memory.items)}
- Extraction strategy: {self.working_memory.extraction_strategy.name}
- Trigger condition: {self.working_memory.extraction_strategy.trigger_condition}
- Priority criteria: {self.working_memory.extraction_strategy.priority_criteria}
- Should extract now: {self.working_memory.should_extract_to_long_term()}
- Last extraction: {self.working_memory.last_extraction or 'Never'}
- Created: {self.working_memory.created_at.strftime('%Y-%m-%d %H:%M:%S')}

RECENT ITEMS (last 5):
"""
            
            recent_items = self.working_memory.get_current_context(5)
            for i, item in enumerate(recent_items[-5:], 1):
                status += f"{i}. [{item.message_type}] {item.content[:60]}... (importance: {item.importance:.2f})\n"
            
            return status
        
        @tool
        async def force_memory_extraction(config: Optional[RunnableConfig] = None) -> str:
            f"""
            Force extraction of memories from working memory to long-term storage.
            
            Use this tool when you determine that important information should be
            preserved immediately, regardless of the extraction strategy's normal triggers.
            
            {strategy_context}
            """
            if not self.working_memory.items:
                return "No items in working memory to extract."
            
            extracted_memories = self.working_memory.extract_to_long_term()
            
            if not extracted_memories:
                return "No memories met the extraction criteria."
            
            # Store extracted memories
            stored_count = 0
            for memory in extracted_memories:
                try:
                    await self.memory_manager.store_memory(
                        content=memory.content,
                        memory_type=memory.memory_type,
                        importance=memory.importance,
                        metadata=memory.metadata
                    )
                    stored_count += 1
                except Exception as e:
                    pass
            
            return f"Forced extraction completed: {stored_count} memories moved to long-term storage."
        
        @tool
        def configure_extraction_strategy(
            strategy_name: str = "message_count",
            message_threshold: int = 10,
            min_importance: float = 0.6,
            config: Optional[RunnableConfig] = None
        ) -> str:
            f"""
            Configure the working memory extraction strategy.
            
            Use this tool to adjust how and when memories are extracted from working
            memory to long-term storage based on the conversation context.
            
            Current strategy: {strategy.name}
            
            Args:
                strategy_name: Name of strategy (currently only 'message_count' supported)
                message_threshold: Number of messages before extraction triggers
                min_importance: Minimum importance score for extraction
            """
            if strategy_name == "message_count":
                new_strategy = MessageCountStrategy(
                    message_threshold=message_threshold,
                    min_importance=min_importance
                )
                self.working_memory.extraction_strategy = new_strategy
                
                return f"""
Extraction strategy updated:
- Strategy: {new_strategy.name}
- Trigger: {new_strategy.trigger_condition}
- Priority: {new_strategy.priority_criteria}
"""
            else:
                return f"Unknown strategy: {strategy_name}. Available strategies: message_count"
        
        return [
            add_memories_to_working_memory,
            create_memory,
            get_working_memory_status,
            force_memory_extraction,
            configure_extraction_strategy
        ]
    
    def get_strategy_context_for_system_prompt(self) -> str:
        """Get strategy context for inclusion in system prompts."""
        strategy = self.working_memory.extraction_strategy
        
        return f"""
MEMORY MANAGEMENT CONTEXT:
You have access to a working memory system with the following configuration:
- Extraction Strategy: {strategy.name}
- Extraction Trigger: {strategy.trigger_condition}
- Priority Criteria: {strategy.priority_criteria}
- Current Working Memory: {len(self.working_memory.items)} items
- Should Extract Now: {self.working_memory.should_extract_to_long_term()}

Use the memory tools intelligently based on this context. Consider:
1. Whether information should go to working memory or directly to long-term storage
2. When to force extraction based on conversation importance
3. How the extraction strategy affects your memory management decisions
"""
