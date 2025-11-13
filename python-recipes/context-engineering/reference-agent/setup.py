#!/usr/bin/env python3
"""
Setup script for the Redis Context Course package.

This package provides a complete reference implementation of a context-aware
AI agent for university course recommendations, demonstrating context engineering
principles using Redis, LangGraph, and OpenAI.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

# Read requirements
requirements = []
with open("requirements.txt", "r") as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="redis-context-course",
    version="1.0.0",
    author="Redis AI Resources Team",
    author_email="redis-ai@redis.com",
    description="Context Engineering with Redis - University Class Agent Reference Implementation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/redis-developer/redis-ai-resources",
    project_urls={
        "Bug Reports": "https://github.com/redis-developer/redis-ai-resources/issues",
        "Source": "https://github.com/redis-developer/redis-ai-resources/tree/main/python-recipes/context-engineering",
        "Documentation": "https://github.com/redis-developer/redis-ai-resources/blob/main/python-recipes/context-engineering/README.md",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Database",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "mypy>=1.5.0",
            "flake8>=6.0.0",
        ],
        "docs": [
            "sphinx>=5.0.0",
            "sphinx-rtd-theme>=1.0.0",
            "myst-parser>=0.18.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "redis-class-agent=redis_context_course.cli:main",
            "generate-courses=redis_context_course.scripts.generate_courses:main",
            "ingest-courses=redis_context_course.scripts.ingest_courses:main",
        ],
    },
    include_package_data=True,
    package_data={
        "redis_context_course": [
            "data/*.json",
            "templates/*.txt",
        ],
    },
    keywords=[
        "redis",
        "ai",
        "context-engineering",
        "langraph",
        "openai",
        "vector-database",
        "semantic-search",
        "memory-management",
        "chatbot",
        "recommendation-system",
    ],
    zip_safe=False,
)
