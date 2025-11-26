import pytest

from redis_context_course import tools as tools_mod
from redis_context_course.agent import ClassAgent


class FakeCourse:
    def __init__(self, code, title, desc, credits=3, fmt="Online", diff="Beginner"):
        self.course_code = code
        self.title = title
        self.description = desc
        self.credits = credits
        self.format = type("Fmt", (), {"value": fmt})
        self.difficulty_level = type("Diff", (), {"value": diff})
        self.prerequisites = []


class FakeCourseManager:
    async def search_courses(self, query: str, limit: int = 5):
        return [
            FakeCourse("CS101", "Intro to CS", "Learn basics of programming"),
            FakeCourse("CS102", "Python Basics", "Introductory Python course"),
        ][:limit]

    async def get_course(self, course_code: str):
        if course_code == "MISSING":
            return None
        return FakeCourse(course_code, "Some Course", "Detailed description")


@pytest.mark.asyncio
async def test_search_courses_tool_formats_result():
    cm = FakeCourseManager()
    (search_tool, get_details_tool, check_prereq_tool) = tools_mod.create_course_tools(
        cm
    )

    out = await search_tool.ainvoke({"query": "python beginner", "limit": 2})
    assert "CS101" in out and "CS102" in out
    assert "Credits:" in out and "Online" in out


@pytest.mark.asyncio
async def test_get_course_details_handles_missing():
    cm = FakeCourseManager()
    (_, get_details_tool, _) = tools_mod.create_course_tools(cm)

    out = await get_details_tool.ainvoke({"course_code": "MISSING"})
    assert "not found" in out.lower()


def test_select_tools_by_keywords():
    tools_map = {
        "search": ["S1"],
        "memory": ["M1"],
    }
    res1 = tools_mod.select_tools_by_keywords("find programming courses", tools_map)
    res2 = tools_mod.select_tools_by_keywords(
        "please remember my preferences", tools_map
    )
    res3 = tools_mod.select_tools_by_keywords("random", tools_map)

    assert res1 == ["S1"]
    assert res2 == ["M1"]
    assert res3 == ["S1"]  # defaults to search


@pytest.mark.asyncio
async def test_summarize_user_knowledge_tool():
    """Test that the user knowledge summary tool is properly integrated."""
    # Test that the tool exists in the agent's tool list
    with pytest.MonkeyPatch().context() as m:
        # Mock the environment variable
        m.setenv("OPENAI_API_KEY", "test-key")

        # Create agent
        agent = ClassAgent("test_user", "test_session")

        # Get the tools
        tools = agent._get_tools()

        # Verify the summarize user knowledge tool is in the list
        tool_names = [tool.name for tool in tools]
        assert "summarize_user_knowledge_tool" in tool_names

        # Find the specific tool
        summary_tool = None
        for tool in tools:
            if tool.name == "summarize_user_knowledge_tool":
                summary_tool = tool
                break

        assert summary_tool is not None
        assert (
            "summarize what the agent knows about the user"
            in summary_tool.description.lower()
        )

        # Test that the tool has the expected properties
        assert hasattr(summary_tool, "ainvoke")
        assert summary_tool.name == "summarize_user_knowledge_tool"


@pytest.mark.asyncio
async def test_summarize_user_knowledge_tool_in_system_prompt():
    """Test that the user knowledge summary tool is mentioned in the system prompt."""
    with pytest.MonkeyPatch().context() as m:
        # Mock the environment variable
        m.setenv("OPENAI_API_KEY", "test-key")

        # Create agent
        agent = ClassAgent("test_user", "test_session")

        # Build system prompt
        context = {"preferences": [], "goals": [], "recent_facts": []}
        system_prompt = agent._build_system_prompt(context)

        # Verify the tool is mentioned in the system prompt
        assert "summarize_user_knowledge" in system_prompt
        assert "comprehensive summary of what you know about the user" in system_prompt


@pytest.mark.asyncio
async def test_clear_user_memories_tool():
    """Test that the clear user memories tool is properly integrated."""
    with pytest.MonkeyPatch().context() as m:
        # Mock the environment variable
        m.setenv("OPENAI_API_KEY", "test-key")

        # Create agent
        agent = ClassAgent("test_user", "test_session")

        # Get the tools
        tools = agent._get_tools()

        # Verify the clear user memories tool is in the list
        tool_names = [tool.name for tool in tools]
        assert "clear_user_memories_tool" in tool_names

        # Find the specific tool
        clear_tool = None
        for tool in tools:
            if tool.name == "clear_user_memories_tool":
                clear_tool = tool
                break

        assert clear_tool is not None
        assert (
            "clear or reset stored user information" in clear_tool.description.lower()
        )

        # Test that the tool has the expected properties
        assert hasattr(clear_tool, "ainvoke")
        assert clear_tool.name == "clear_user_memories_tool"
