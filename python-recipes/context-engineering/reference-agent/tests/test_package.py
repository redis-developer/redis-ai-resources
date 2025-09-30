"""
Basic tests to verify the package structure and imports work correctly.
"""

import pytest


def test_package_imports():
    """Test that the main package imports work correctly."""
    try:
        import redis_context_course
        assert redis_context_course.__version__ == "1.0.0"
        assert redis_context_course.__author__ == "Redis AI Resources Team"
    except ImportError as e:
        pytest.fail(f"Failed to import redis_context_course: {e}")


def test_model_imports():
    """Test that model imports work correctly."""
    try:
        from redis_context_course.models import (
            Course, StudentProfile, DifficultyLevel, CourseFormat
        )
        
        # Test enum values
        assert DifficultyLevel.BEGINNER == "beginner"
        assert CourseFormat.ONLINE == "online"
        
    except ImportError as e:
        pytest.fail(f"Failed to import models: {e}")


def test_manager_imports():
    """Test that manager imports work correctly."""
    try:
        from redis_context_course.memory_client import MemoryClient
        from redis_context_course.course_manager import CourseManager
        from redis_context_course.redis_config import RedisConfig

        # Test that classes can be instantiated (without Redis connection)
        assert MemoryClient is not None
        assert CourseManager is not None
        assert RedisConfig is not None

    except ImportError as e:
        pytest.fail(f"Failed to import managers: {e}")


def test_agent_imports():
    """Test that agent imports work correctly."""
    try:
        from redis_context_course.agent import ClassAgent, AgentState
        
        assert ClassAgent is not None
        assert AgentState is not None
        
    except ImportError as e:
        pytest.fail(f"Failed to import agent: {e}")


def test_scripts_imports():
    """Test that script imports work correctly."""
    try:
        from redis_context_course.scripts import generate_courses, ingest_courses
        
        assert generate_courses is not None
        assert ingest_courses is not None
        
    except ImportError as e:
        pytest.fail(f"Failed to import scripts: {e}")


def test_cli_imports():
    """Test that CLI imports work correctly."""
    try:
        from redis_context_course import cli

        assert cli is not None
        assert hasattr(cli, 'main')

    except ImportError as e:
        pytest.fail(f"Failed to import CLI: {e}")


def test_tools_imports():
    """Test that tools module imports work correctly."""
    try:
        from redis_context_course.tools import (
            create_course_tools,
            create_memory_tools,
            select_tools_by_keywords
        )

        assert create_course_tools is not None
        assert create_memory_tools is not None
        assert select_tools_by_keywords is not None

    except ImportError as e:
        pytest.fail(f"Failed to import tools: {e}")


def test_optimization_helpers_imports():
    """Test that optimization helpers import work correctly."""
    try:
        from redis_context_course.optimization_helpers import (
            count_tokens,
            estimate_token_budget,
            hybrid_retrieval,
            create_summary_view,
            filter_tools_by_intent,
            format_context_for_llm
        )

        assert count_tokens is not None
        assert estimate_token_budget is not None
        assert hybrid_retrieval is not None
        assert create_summary_view is not None
        assert filter_tools_by_intent is not None
        assert format_context_for_llm is not None

    except ImportError as e:
        pytest.fail(f"Failed to import optimization helpers: {e}")


def test_count_tokens_basic():
    """Test basic token counting functionality."""
    try:
        from redis_context_course.optimization_helpers import count_tokens

        # Test with simple text
        text = "Hello, world!"
        tokens = count_tokens(text)

        assert isinstance(tokens, int)
        assert tokens > 0

    except Exception as e:
        pytest.fail(f"Token counting failed: {e}")


def test_filter_tools_by_intent_basic():
    """Test basic tool filtering functionality."""
    try:
        from redis_context_course.optimization_helpers import filter_tools_by_intent

        # Mock tool groups
        tool_groups = {
            "search": ["search_tool"],
            "memory": ["memory_tool"],
        }

        # Test search intent
        result = filter_tools_by_intent("find courses", tool_groups)
        assert result == ["search_tool"]

        # Test memory intent
        result = filter_tools_by_intent("remember this", tool_groups)
        assert result == ["memory_tool"]

    except Exception as e:
        pytest.fail(f"Tool filtering failed: {e}")


if __name__ == "__main__":
    pytest.main([__file__])
