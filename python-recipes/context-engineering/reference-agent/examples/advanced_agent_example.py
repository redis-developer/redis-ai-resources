"""
Advanced Agent Example

This example demonstrates patterns from all sections of the Context Engineering course:
- Section 2: System context and tools
- Section 3: Memory management
- Section 4: Optimizations (token management, retrieval strategies, tool filtering)

This is a production-ready pattern that combines all the techniques.
"""

import asyncio

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from redis_context_course import (
    CourseManager,
    MemoryClient,
    create_course_tools,
    create_memory_tools,
    create_summary_view,
    estimate_token_budget,
    filter_tools_by_intent,
    format_context_for_llm,
)


class AdvancedClassAgent:
    """
    Advanced class scheduling agent with all optimizations.

    Features:
    - Tool filtering based on intent
    - Token budget management
    - Hybrid retrieval (summary + specific items)
    - Memory integration
    - Grounding support
    """

    def __init__(
        self,
        student_id: str,
        session_id: str = "default_session",
        model: str = "gpt-4o",
        enable_tool_filtering: bool = True,
        enable_memory_tools: bool = False,
    ):
        self.student_id = student_id
        self.session_id = session_id
        self.llm = ChatOpenAI(model=model, temperature=0.7)
        self.course_manager = CourseManager()
        self.memory_client = MemoryClient(
            user_id=student_id, namespace="redis_university"
        )

        # Configuration
        self.enable_tool_filtering = enable_tool_filtering
        self.enable_memory_tools = enable_memory_tools

        # Create tools
        self.course_tools = create_course_tools(self.course_manager)
        self.memory_tools = (
            create_memory_tools(
                self.memory_client, session_id=self.session_id, user_id=self.student_id
            )
            if enable_memory_tools
            else []
        )

        # Organize tools by category (for filtering)
        self.tool_groups = {
            "search": self.course_tools,
            "memory": self.memory_tools,
        }

        # Pre-compute course catalog summary (Section 4 pattern)
        self.catalog_summary = None

    async def initialize(self):
        """Initialize the agent (pre-compute summaries)."""
        # Create course catalog summary
        all_courses = await self.course_manager.get_all_courses()
        self.catalog_summary = await create_summary_view(
            items=all_courses, group_by_field="department", max_items_per_group=5
        )
        print(f"✅ Agent initialized with {len(all_courses)} courses")

    async def chat(
        self, user_message: str, session_id: str, conversation_history: list = None
    ) -> tuple[str, list]:
        """
        Process a user message with all optimizations.

        Args:
            user_message: User's message
            session_id: Session ID for working memory
            conversation_history: Previous messages in this session

        Returns:
            Tuple of (response, updated_conversation_history)
        """
        if conversation_history is None:
            conversation_history = []

        # Step 1: Load working memory
        working_memory = await self.memory_client.get_working_memory(
            session_id=session_id, model_name="gpt-4o"
        )

        # Step 2: Search long-term memory for relevant context
        long_term_memories = await self.memory_client.search_memories(
            query=user_message, limit=5
        )

        # Step 3: Build context (Section 4 pattern)
        system_prompt = self._build_system_prompt(long_term_memories)

        # Step 4: Estimate token budget (Section 4 pattern)
        token_budget = estimate_token_budget(
            system_prompt=system_prompt,
            working_memory_messages=len(working_memory.messages)
            if working_memory
            else 0,
            long_term_memories=len(long_term_memories),
            retrieved_context_items=0,  # Will add if we do RAG
        )

        print(f"\n📊 Token Budget:")
        print(f"   System: {token_budget['system_prompt']}")
        print(f"   Working Memory: {token_budget['working_memory']}")
        print(f"   Long-term Memory: {token_budget['long_term_memory']}")
        print(f"   Total: {token_budget['total_input']} tokens")

        # Step 5: Select tools based on intent (Section 4 pattern)
        if self.enable_tool_filtering:
            relevant_tools = filter_tools_by_intent(
                query=user_message, tool_groups=self.tool_groups, default_group="search"
            )
            print(f"\n🔧 Selected {len(relevant_tools)} relevant tools")
        else:
            relevant_tools = self.course_tools + self.memory_tools
            print(f"\n🔧 Using all {len(relevant_tools)} tools")

        # Step 6: Bind tools and invoke LLM
        llm_with_tools = self.llm.bind_tools(relevant_tools)

        # Build messages
        messages = [SystemMessage(content=system_prompt)]

        # Add working memory
        if working_memory and working_memory.messages:
            for msg in working_memory.messages:
                if msg.role == "user":
                    messages.append(HumanMessage(content=msg.content))
                elif msg.role == "assistant":
                    messages.append(AIMessage(content=msg.content))

        # Add current message
        messages.append(HumanMessage(content=user_message))

        # Get response
        response = llm_with_tools.invoke(messages)

        # Handle tool calls if any
        if response.tool_calls:
            print(f"\n🛠️  Agent called {len(response.tool_calls)} tool(s)")
            # In a full implementation, you'd execute tools here
            # For this example, we'll just note them
            for tool_call in response.tool_calls:
                print(f"   - {tool_call['name']}")

        # Step 7: Save to working memory (triggers automatic extraction)
        conversation_history.append(HumanMessage(content=user_message))
        conversation_history.append(AIMessage(content=response.content))

        messages_to_save = [
            {
                "role": "user" if isinstance(m, HumanMessage) else "assistant",
                "content": m.content,
            }
            for m in conversation_history
        ]

        await self.memory_client.save_working_memory(
            session_id=session_id, messages=messages_to_save
        )

        return response.content, conversation_history

    def _build_system_prompt(self, long_term_memories: list) -> str:
        """
        Build system prompt with all context.

        This uses the format_context_for_llm pattern from Section 4.
        """
        base_instructions = """You are a helpful class scheduling agent for Redis University.
Help students find courses, check prerequisites, and plan their schedule.

Use the available tools to search courses and check prerequisites.
Be friendly, helpful, and personalized based on what you know about the student.
"""

        # Format memories
        memory_context = None
        if long_term_memories:
            memory_lines = [f"- {m.text}" for m in long_term_memories]
            memory_context = "What you know about this student:\n" + "\n".join(
                memory_lines
            )

        # Use the formatting helper
        return format_context_for_llm(
            system_instructions=base_instructions,
            summary_view=self.catalog_summary,
            memories=memory_context,
        )


async def main():
    """Run the advanced agent example."""
    print("=" * 80)
    print("ADVANCED CLASS AGENT EXAMPLE")
    print("=" * 80)

    # Initialize agent
    agent = AdvancedClassAgent(
        student_id="demo_student",
        enable_tool_filtering=True,
        enable_memory_tools=False,  # Set to True to give LLM control over memory
    )

    await agent.initialize()

    # Simulate a conversation
    session_id = "demo_session"
    conversation = []

    queries = [
        "Hi! I'm interested in machine learning courses.",
        "What are the prerequisites for CS401?",
        "I've completed CS101 and CS201. Can I take CS401?",
    ]

    for i, query in enumerate(queries, 1):
        print(f"\n{'=' * 80}")
        print(f"TURN {i}")
        print(f"{'=' * 80}")
        print(f"\n👤 User: {query}")

        response, conversation = await agent.chat(
            user_message=query, session_id=session_id, conversation_history=conversation
        )

        print(f"\n🤖 Agent: {response}")

        # Small delay between turns
        await asyncio.sleep(1)

    print(f"\n{'=' * 80}")
    print("✅ Conversation complete!")
    print(f"{'=' * 80}")

    # Show final statistics
    print("\n📈 Final Statistics:")
    print(f"   Turns: {len(queries)}")
    print(f"   Messages in conversation: {len(conversation)}")

    # Check what was extracted to long-term memory
    print("\n🧠 Checking long-term memory...")
    await asyncio.sleep(2)  # Wait for extraction

    memories = await agent.memory_client.search_memories(query="", limit=10)

    if memories:
        print(f"   Extracted {len(memories)} memories:")
        for memory in memories:
            print(f"   - {memory.text}")
    else:
        print("   No memories extracted yet (may take a moment)")


if __name__ == "__main__":
    asyncio.run(main())
