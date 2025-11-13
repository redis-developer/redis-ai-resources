import asyncio
import pytest

from redis_context_course import tools as tools_mod


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
    (search_tool, get_details_tool, check_prereq_tool) = tools_mod.create_course_tools(cm)

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
    res2 = tools_mod.select_tools_by_keywords("please remember my preferences", tools_map)
    res3 = tools_mod.select_tools_by_keywords("random", tools_map)

    assert res1 == ["S1"]
    assert res2 == ["M1"]
    assert res3 == ["S1"]  # defaults to search

