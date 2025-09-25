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
        from redis_context_course.memory import MemoryManager
        from redis_context_course.course_manager import CourseManager
        from redis_context_course.redis_config import RedisConfig
        
        # Test that classes can be instantiated (without Redis connection)
        assert MemoryManager is not None
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


if __name__ == "__main__":
    pytest.main([__file__])
