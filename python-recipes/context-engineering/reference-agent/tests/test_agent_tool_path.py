import asyncio
import os
import types
import pytest

from langchain_core.messages import AIMessage

# Import module under test
from redis_context_course import agent as agent_mod
from redis_context_course.redis_config import redis_config
from redis_context_course.course_manager import CourseManager
from redis_context_course.models import (
    Course,
    DifficultyLevel,
    CourseFormat,
    CourseSchedule,
)


class FakeMemoryClient:
    def __init__(self, config):
        self.config = config
        self.put_calls = []

    async def get_or_create_working_memory(self, session_id: str, user_id: str, model_name: str):
        wm = types.SimpleNamespace(messages=[])
        return True, wm

    async def search_long_term_memory(self, text: str, user_id, limit: int = 5):
        return types.SimpleNamespace(memories=[])

    async def put_working_memory(self, session_id: str, memory, user_id: str, model_name: str):
        self.put_calls.append({
            "session_id": session_id,
            "user_id": user_id,
            "model_name": model_name,
            "message_count": len(getattr(memory, "messages", [])),
        })
        return True


class ToolCallingLLM:
    """A minimal LLM stub that first requests a tool, then returns a normal answer."""
    def __init__(self, model: str, temperature: float = 0.7):
        self.model = model
        self.temperature = temperature
        self._call_num = 0

    def bind_tools(self, tools):
        # LangGraph/ToolNode will handle calling the tool
        return self

    async def ainvoke(self, messages):
        self._call_num += 1
        if self._call_num == 1:
            # Ask to call the agent's _search_courses_tool (LangChain expects an id field)
            return AIMessage(
                content="",
                tool_calls=[{"id": "call_1", "name": "_search_courses_tool", "args": {"query": "python", "filters": {}}}],
            )
        # After the tool runs, return a normal assistant message
        return AIMessage(content="Here are some relevant Python courses.")


@pytest.mark.asyncio
async def test_agent_executes_tool_path_with_real_redis(redis_stack_url, monkeypatch):
    # Point the agent at the Testcontainers Redis 8 instance
    monkeypatch.setenv("REDIS_URL", redis_stack_url)

    # Reinitialize redis_config so it connects to the container, not any cached client
    redis_config.cleanup()
    redis_config._redis_client = None
    redis_config._vector_index = None

    # Avoid real OpenAI calls: make embeddings deterministic
    async def fake_embed_query(text: str):
        # Use a constant non-zero vector to ensure cosine similarity works
        return [1.0] * 1536

    # Provide a dummy embeddings instance to avoid OpenAI calls
    class _DummyEmb:
        async def aembed_query(self, text: str):
            return [1.0] * 1536
    redis_config._embeddings = _DummyEmb()

    # Seed a course into Redis via the real CourseManager and real index
    cm = CourseManager()
    course = Course(
        id="c1",
        course_code="CS101",
        title="Python Basics",
        description="Introductory Python programming",
        department="CS",
        major="CS",
        difficulty_level=DifficultyLevel.BEGINNER,
        format=CourseFormat.ONLINE,
        semester="fall",
        year=2025,
        credits=3,
        tags=["python", "programming"],
        instructor="Dr. Py",
        max_enrollment=100,
        current_enrollment=0,
        learning_objectives=["Variables", "Loops"],
        prerequisites=[],
        schedule=CourseSchedule(days=["monday"], start_time="09:00", end_time="10:00"),
    )
    await cm.store_course(course)

    # Patch Memory API client (we are only avoiding the network service; Redis is real)
    monkeypatch.setattr(agent_mod, "MemoryAPIClient", FakeMemoryClient)
    # Patch LLM to drive tool path
    monkeypatch.setattr(agent_mod, "ChatOpenAI", ToolCallingLLM)

    a = agent_mod.ClassAgent("student_tool_path")
    result = await a.chat("Find beginner Python courses")

    # Validate final response and that memory was saved
    assert "Python" in result or "courses" in result
    mc: FakeMemoryClient = a.memory_client  # type: ignore
    assert len(mc.put_calls) == 1
    assert mc.put_calls[0]["session_id"] == a.session_id
    assert mc.put_calls[0]["user_id"] == a.student_id
    assert mc.put_calls[0]["message_count"] >= 2

