import types

import pytest
from langchain_core.messages import AIMessage

# Target under test
from redis_context_course import agent as agent_mod


class FakeMemoryClient:
    def __init__(self, config):
        self.config = config
        self.put_calls = []

    async def get_or_create_working_memory(
        self, session_id: str, user_id: str, model_name: str
    ):
        # Return a simple object with .messages list
        wm = types.SimpleNamespace(messages=[])
        return True, wm

    async def search_long_term_memory(self, text: str, user_id, limit: int = 5):
        # Return an object with .memories to mimic client result
        return types.SimpleNamespace(memories=[])

    async def put_working_memory(
        self, session_id: str, memory, user_id: str, model_name: str
    ):
        self.put_calls.append(
            {
                "session_id": session_id,
                "user_id": user_id,
                "model_name": model_name,
                "message_count": len(getattr(memory, "messages", [])),
            }
        )
        return True


class FakeLLM:
    def __init__(self, model: str, temperature: float = 0.7):
        self.model = model
        self.temperature = temperature

    def bind_tools(self, tools):
        # Return self to support .ainvoke(messages)
        return self

    async def ainvoke(self, messages):
        # Return a basic AIMessage without tool calls
        return AIMessage(content="TEST_RESPONSE")


class FakeCourseManager:
    def __init__(self):
        pass


@pytest.mark.asyncio
async def test_agent_chat_returns_llm_response_and_saves_memory(monkeypatch):
    # Patch heavy dependencies used inside the agent module
    monkeypatch.setattr(agent_mod, "MemoryAPIClient", FakeMemoryClient)
    monkeypatch.setattr(agent_mod, "ChatOpenAI", FakeLLM)
    monkeypatch.setattr(agent_mod, "CourseManager", FakeCourseManager)

    # Ensure env var is set but the value won't be used due to mocks
    monkeypatch.setenv("AGENT_MEMORY_URL", "http://localhost:8088")

    a = agent_mod.ClassAgent("student_test")
    result = await a.chat("hello")

    assert result == "TEST_RESPONSE"

    # Verify working memory save happened
    mc: FakeMemoryClient = a.memory_client  # type: ignore
    assert len(mc.put_calls) == 1
    assert mc.put_calls[0]["session_id"] == a.session_id
    assert mc.put_calls[0]["user_id"] == a.student_id
    # Should have at least 2 messages (user + assistant)
    assert mc.put_calls[0]["message_count"] >= 2
