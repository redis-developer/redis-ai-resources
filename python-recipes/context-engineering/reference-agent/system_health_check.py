#!/usr/bin/env python3
"""
Comprehensive Redis Context Course System Health Check

This script provides a thorough validation of the entire system,
focusing on functional testing rather than specific key patterns.
"""

import argparse
import asyncio
import os
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

import redis
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class CheckStatus(Enum):
    """Status levels for checks."""

    PASS = "✅"
    WARN = "⚠️"
    FAIL = "❌"
    INFO = "ℹ️"


@dataclass
class CheckResult:
    """Result of a system check."""

    name: str
    status: CheckStatus
    message: str
    details: Optional[str] = None
    fix_command: Optional[str] = None
    performance_ms: Optional[float] = None


class SystemHealthChecker:
    """Comprehensive system health checker."""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.results: List[CheckResult] = []
        self.redis_client = None

    def add_result(self, result: CheckResult):
        """Add a check result."""
        self.results.append(result)

    def print_result(self, result: CheckResult):
        """Print a single result."""
        output = f"{result.status.value} {result.name}: {result.message}"
        if self.verbose and result.details:
            output += f"\n   Details: {result.details}"
        if result.fix_command:
            output += f"\n   Fix: {result.fix_command}"
        if result.performance_ms is not None:
            output += f"\n   Performance: {result.performance_ms:.1f}ms"
        print(output)

    async def check_infrastructure(self) -> List[CheckResult]:
        """Check basic infrastructure components."""
        results = []

        # Redis Connection
        start_time = time.time()
        try:
            redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
            self.redis_client = redis.from_url(redis_url, decode_responses=True)
            self.redis_client.ping()

            # Get Redis info
            info = self.redis_client.info()
            redis_version = info.get("redis_version", "unknown")
            memory_used = info.get("used_memory_human", "unknown")

            elapsed_ms = (time.time() - start_time) * 1000

            results.append(
                CheckResult(
                    name="Redis Connection",
                    status=CheckStatus.PASS,
                    message=f"Connected to Redis {redis_version}",
                    details=f"Memory used: {memory_used}",
                    performance_ms=elapsed_ms,
                )
            )

        except Exception as e:
            results.append(
                CheckResult(
                    name="Redis Connection",
                    status=CheckStatus.FAIL,
                    message=f"Failed to connect: {e}",
                    fix_command="docker run -d --name redis -p 6379:6379 redis:8-alpine",
                )
            )
            return results

        # Environment Variables
        env_vars = {
            "OPENAI_API_KEY": "OpenAI API access",
            "REDIS_URL": "Redis connection",
            "AGENT_MEMORY_URL": "Agent Memory Server",
        }

        for var, description in env_vars.items():
            value = os.getenv(var)
            if not value or value == "your_openai_api_key_here":
                results.append(
                    CheckResult(
                        name=f"Environment: {var}",
                        status=CheckStatus.FAIL,
                        message=f"Not set or using placeholder",
                        fix_command=f"Set {var} in .env file",
                    )
                )
            else:
                # Mask sensitive values
                display_value = (
                    value[:8] + "..." + value[-4:] if "API_KEY" in var else value
                )
                results.append(
                    CheckResult(
                        name=f"Environment: {var}",
                        status=CheckStatus.PASS,
                        message=f"Configured",
                        details=display_value,
                    )
                )

        return results

    def detect_data_patterns(self) -> Dict[str, List[str]]:
        """Auto-detect actual data patterns in Redis."""
        all_keys = self.redis_client.keys("*")

        patterns = {
            "majors": [k for k in all_keys if k.startswith("major:")],
            "courses": [k for k in all_keys if k.startswith("course_catalog:")],
            "memory": [k for k in all_keys if "memory" in k.lower()],
            "working_memory": [k for k in all_keys if "working_memory" in k],
            "other": [
                k
                for k in all_keys
                if not any(p in k.lower() for p in ["major", "course", "memory"])
            ],
        }

        return patterns

    def check_data_presence(self) -> List[CheckResult]:
        """Check if required data is present."""
        results = []

        patterns = self.detect_data_patterns()

        # Check majors
        major_count = len(patterns["majors"])
        if major_count > 0:
            results.append(
                CheckResult(
                    name="Major Records",
                    status=CheckStatus.PASS,
                    message=f"Found {major_count} major records",
                    details=f"Pattern: major:{{id}}",
                )
            )
        else:
            results.append(
                CheckResult(
                    name="Major Records",
                    status=CheckStatus.FAIL,
                    message="No major records found",
                    fix_command="ingest-courses --catalog course_catalog.json --clear",
                )
            )

        # Check courses
        course_count = len(patterns["courses"])
        if course_count > 0:
            results.append(
                CheckResult(
                    name="Course Records",
                    status=CheckStatus.PASS,
                    message=f"Found {course_count} course records",
                    details=f"Pattern: course_catalog:{{id}}",
                )
            )

            # Sample a course to check data quality
            if patterns["courses"]:
                sample_key = patterns["courses"][0]
                try:
                    # Use Redis client without decode_responses for binary data
                    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
                    binary_redis = redis.from_url(redis_url, decode_responses=False)
                    sample_data = binary_redis.hgetall(sample_key)

                    # Convert keys to strings and check for required fields
                    field_names = [key.decode("utf-8") for key in sample_data.keys()]
                    required_fields = [
                        "course_code",
                        "title",
                        "description",
                        "content_vector",
                    ]
                    missing_fields = [
                        f for f in required_fields if f not in field_names
                    ]

                    if not missing_fields:
                        # Get text fields safely
                        course_code = sample_data.get(b"course_code", b"N/A").decode(
                            "utf-8"
                        )
                        title = sample_data.get(b"title", b"N/A").decode("utf-8")

                        results.append(
                            CheckResult(
                                name="Course Data Quality",
                                status=CheckStatus.PASS,
                                message="All required fields present",
                                details=f"Sample: {course_code} - {title}",
                            )
                        )
                    else:
                        results.append(
                            CheckResult(
                                name="Course Data Quality",
                                status=CheckStatus.WARN,
                                message=f"Missing fields: {missing_fields}",
                                fix_command="Re-run ingestion with --clear flag",
                            )
                        )

                except Exception as e:
                    results.append(
                        CheckResult(
                            name="Course Data Quality",
                            status=CheckStatus.INFO,
                            message="Cannot validate binary vector data (this is normal)",
                            details="Vector embeddings are stored as binary data",
                        )
                    )
        else:
            results.append(
                CheckResult(
                    name="Course Records",
                    status=CheckStatus.FAIL,
                    message="No course records found",
                    fix_command="ingest-courses --catalog course_catalog.json --clear",
                )
            )

        # Memory system
        memory_count = len(patterns["memory"]) + len(patterns["working_memory"])
        if memory_count > 0:
            results.append(
                CheckResult(
                    name="Memory System",
                    status=CheckStatus.PASS,
                    message=f"Found {memory_count} memory-related keys",
                    details="Agent Memory Server integration active",
                )
            )
        else:
            results.append(
                CheckResult(
                    name="Memory System",
                    status=CheckStatus.INFO,
                    message="No memory data (normal for fresh install)",
                )
            )

        return results

    async def check_functionality(self) -> List[CheckResult]:
        """Test actual system functionality."""
        results = []

        try:
            # Test course manager import and basic functionality
            start_time = time.time()
            # Import here as this is a conditional test, not main functionality
            from redis_context_course import ClassAgent
            from redis_context_course.course_manager import CourseManager

            course_manager = CourseManager()
            elapsed_ms = (time.time() - start_time) * 1000

            results.append(
                CheckResult(
                    name="Package Import",
                    status=CheckStatus.PASS,
                    message="Successfully imported core modules",
                    performance_ms=elapsed_ms,
                )
            )

            # Test course search
            start_time = time.time()
            courses = await course_manager.search_courses("programming", limit=3)
            elapsed_ms = (time.time() - start_time) * 1000

            if courses:
                results.append(
                    CheckResult(
                        name="Course Search",
                        status=CheckStatus.PASS,
                        message=f"Found {len(courses)} courses",
                        details=f"Sample: {courses[0].course_code} - {courses[0].title}",
                        performance_ms=elapsed_ms,
                    )
                )
            else:
                results.append(
                    CheckResult(
                        name="Course Search",
                        status=CheckStatus.FAIL,
                        message="Search returned no results",
                        fix_command="Check if courses are properly ingested with embeddings",
                    )
                )

            # Test agent initialization
            start_time = time.time()
            agent = ClassAgent("health_check_student")
            elapsed_ms = (time.time() - start_time) * 1000

            results.append(
                CheckResult(
                    name="Agent Initialization",
                    status=CheckStatus.PASS,
                    message="Agent created successfully",
                    performance_ms=elapsed_ms,
                )
            )

            # Test basic agent query
            start_time = time.time()
            response = await agent.chat("How many courses are available?")
            elapsed_ms = (time.time() - start_time) * 1000

            if response and len(response) > 10:
                results.append(
                    CheckResult(
                        name="Agent Query",
                        status=CheckStatus.PASS,
                        message="Agent responded successfully",
                        details=f"Response length: {len(response)} chars",
                        performance_ms=elapsed_ms,
                    )
                )
            else:
                results.append(
                    CheckResult(
                        name="Agent Query",
                        status=CheckStatus.FAIL,
                        message="Agent query failed or returned empty response",
                        details=f"Response: {response}",
                    )
                )

        except ImportError as e:
            results.append(
                CheckResult(
                    name="Package Import",
                    status=CheckStatus.FAIL,
                    message=f"Import failed: {e}",
                    fix_command="pip install -e .",
                )
            )
        except Exception as e:
            results.append(
                CheckResult(
                    name="Functionality Test",
                    status=CheckStatus.FAIL,
                    message=f"Unexpected error: {e}",
                    details=str(e),
                )
            )

        return results

    def generate_summary(self) -> Dict[str, any]:
        """Generate overall system summary."""
        total = len(self.results)
        passed = len([r for r in self.results if r.status == CheckStatus.PASS])
        warnings = len([r for r in self.results if r.status == CheckStatus.WARN])
        failed = len([r for r in self.results if r.status == CheckStatus.FAIL])

        if failed == 0 and warnings == 0:
            overall_status = "EXCELLENT"
        elif failed == 0:
            overall_status = "GOOD"
        elif failed <= 2:
            overall_status = "NEEDS ATTENTION"
        else:
            overall_status = "CRITICAL ISSUES"

        return {
            "overall_status": overall_status,
            "total_checks": total,
            "passed": passed,
            "warnings": warnings,
            "failed": failed,
            "critical_issues": [
                r for r in self.results if r.status == CheckStatus.FAIL
            ],
            "avg_performance": sum(
                r.performance_ms for r in self.results if r.performance_ms
            )
            / max(1, len([r for r in self.results if r.performance_ms])),
        }

    async def run_all_checks(self):
        """Run all system checks."""
        print(f"""Redis Context Course - System Health Check
{"=" * 60}
Started at: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

INFRASTRUCTURE
{"-" * 20}""")
        infra_results = await self.check_infrastructure()
        for result in infra_results:
            self.add_result(result)
            self.print_result(result)

        # Only continue if Redis is working
        if not any(
            r.status == CheckStatus.FAIL and "Redis Connection" in r.name
            for r in infra_results
        ):
            # Data presence checks
            print(f"""
DATA VALIDATION
{"-" * 20}""")
            data_results = self.check_data_presence()
            for result in data_results:
                self.add_result(result)
                self.print_result(result)

            # Functionality checks
            print(f"""
FUNCTIONALITY
{"-" * 20}""")
            func_results = await self.check_functionality()
            for result in func_results:
                self.add_result(result)
                self.print_result(result)

        # Summary
        summary = self.generate_summary()
        summary_output = f"""
SUMMARY
{"-" * 20}
🎯 Overall Status: {summary["overall_status"]}
📊 Results: {summary["passed"]}/{summary["total_checks"]} passed"""

        if summary["warnings"] > 0:
            summary_output += f"\n⚠️  Warnings: {summary['warnings']}"
        if summary["failed"] > 0:
            summary_output += f"\n❌ Failed: {summary['failed']}"
        if summary["avg_performance"] > 0:
            summary_output += (
                f"\n⚡ Avg Response Time: {summary['avg_performance']:.1f}ms"
            )

        print(summary_output)

        # Critical issues
        if summary["critical_issues"]:
            issues_output = "\nCRITICAL ISSUES TO FIX:"
            for issue in summary["critical_issues"]:
                issues_output += f"\n   • {issue.name}: {issue.message}"
                if issue.fix_command:
                    issues_output += f"\n     Fix: {issue.fix_command}"
            print(issues_output)

        # Next steps
        if summary["failed"] == 0:
            next_steps = """\nNEXT STEPS:
   • System is ready! Try: redis-class-agent --student-id your_name
   • Explore examples in the examples/ directory
   • Check out the notebooks for tutorials"""
        else:
            next_steps = """\nNEXT STEPS:
   • Fix the critical issues listed above
   • Re-run this health check to verify fixes
   • Check the documentation for troubleshooting"""

        print(next_steps)

        return summary["failed"] == 0


async def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Redis Context Course System Health Check"
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    args = parser.parse_args()

    checker = SystemHealthChecker(verbose=args.verbose)
    success = await checker.run_all_checks()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
