#!/usr/bin/env python3
"""
CLI for Stage 2 Context-Engineered Agent.

Usage:
    # Interactive mode
    python cli.py

    # Single query
    python cli.py "What machine learning courses are available?"

    # Simulation mode (run example queries)
    python cli.py --simulate

    # Cleanup courses on exit
    python cli.py --cleanup
"""

import os
import sys
import asyncio
import atexit
import logging
from pathlib import Path
from typing import Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

# Load environment variables from reference-agent/.env
from dotenv import load_dotenv
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(env_path)

from redis_context_course import CourseManager
from agent import setup_agent, cleanup_courses, initialize_state

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(name)-20s %(levelname)-8s %(message)s',
    datefmt='%H:%M:%S'
)

logger = logging.getLogger("stage2-cli")


class ContextEngineeredCLI:
    """
    CLI for Stage 2 Context-Engineered Agent.

    Provides interactive mode, single query mode, and simulation mode.
    """

    def __init__(self, cleanup_on_exit: bool = False):
        """
        Initialize CLI.

        Args:
            cleanup_on_exit: If True, remove courses from Redis on exit
        """
        self.workflow = None
        self.course_manager = None
        self.cleanup_on_exit = cleanup_on_exit

        # Register cleanup handler
        if cleanup_on_exit:
            atexit.register(self._cleanup)

    def _cleanup(self):
        """Cleanup courses on exit if requested."""
        if self.course_manager and self.cleanup_on_exit:
            logger.info("\n🧹 Cleaning up courses...")
            asyncio.run(cleanup_courses(self.course_manager))

    def initialize(self):
        """Initialize the agent."""
        logger.info("=" * 60)
        logger.info("Stage 2: Context-Engineered Agent")
        logger.info("=" * 60)
        logger.info("")

        # Setup agent
        self.workflow, self.course_manager = setup_agent(auto_load_courses=True)

        if self.cleanup_on_exit:
            logger.info("🧹 Courses will be cleaned up on exit")
        else:
            logger.info("💾 Courses will persist in Redis after exit")

        logger.info("")

    def ask_question(self, query: str) -> dict:
        """
        Ask a question and get an answer.

        Args:
            query: User's question

        Returns:
            Result dictionary with answer and metadata
        """
        logger.info(f"❓ Question: {query}")
        logger.info("")

        # Initialize state
        state = initialize_state(query)

        # Run workflow
        result = self.workflow.invoke(state)

        return result

    def print_result(self, result: dict):
        """
        Print the result in a formatted way.

        Args:
            result: Result dictionary from workflow
        """
        logger.info("")
        logger.info("=" * 60)
        logger.info("📝 Answer:")
        logger.info("=" * 60)
        print(result["final_answer"])
        print()

        # Print metrics
        logger.info("=" * 60)
        logger.info("📊 Metrics:")
        logger.info("=" * 60)
        logger.info(f"   Courses Found: {result['courses_found']}")
        if result.get('total_tokens'):
            logger.info(f"   Estimated Tokens: ~{result['total_tokens']}")
        logger.info("")
        logger.info("✨ Context engineering applied:")
        logger.info("   - Cleaned: Removed noise fields")
        logger.info("   - Transformed: JSON → natural text")
        logger.info("   - Optimized: Efficient token usage")
        logger.info("")
        logger.info("💡 Compare with Stage 1 to see the improvements!")
        logger.info("")

    def interactive_mode(self):
        """Run in interactive mode."""
        self.initialize()

        logger.info("💬 Interactive Mode")
        logger.info("   Type your questions (or 'quit' to exit)")
        logger.info("")

        while True:
            try:
                query = input("You: ").strip()

                if not query:
                    continue

                if query.lower() in ['quit', 'exit', 'q']:
                    logger.info("👋 Goodbye!")
                    break

                result = self.ask_question(query)
                self.print_result(result)

            except KeyboardInterrupt:
                logger.info("\n👋 Goodbye!")
                break
            except Exception as e:
                logger.error(f"Error: {e}")
                import traceback
                traceback.print_exc()

    def single_query_mode(self, query: str):
        """Run a single query."""
        self.initialize()

        result = self.ask_question(query)
        self.print_result(result)

    def simulation_mode(self):
        """Run simulation with example queries."""
        self.initialize()

        logger.info("🎬 Simulation Mode - Running Example Queries")
        logger.info("")

        example_queries = [
            "What machine learning courses are available?",
            "What are beginner-level computer science courses?",
            "Which courses teach Python programming?",
        ]

        for i, query in enumerate(example_queries, 1):
            logger.info(f"\n{'=' * 60}")
            logger.info(f"Example {i}/{len(example_queries)}")
            logger.info(f"{'=' * 60}\n")

            result = self.ask_question(query)
            self.print_result(result)

            if i < len(example_queries):
                logger.info("Press Enter to continue...")
                input()


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Stage 2 Context-Engineered Agent - Applies Section 2 Techniques"
    )
    parser.add_argument(
        "query",
        nargs="?",
        help="Question to ask (if not provided, runs in interactive mode)"
    )
    parser.add_argument(
        "--simulate",
        action="store_true",
        help="Run simulation mode with example queries"
    )
    parser.add_argument(
        "--cleanup",
        action="store_true",
        help="Remove courses from Redis on exit"
    )
    parser.add_argument(
        "--no-cleanup",
        action="store_true",
        help="Keep courses in Redis after exit (default)"
    )

    args = parser.parse_args()

    # Determine cleanup behavior
    cleanup = args.cleanup and not args.no_cleanup

    # Create CLI
    cli = ContextEngineeredCLI(cleanup_on_exit=cleanup)

    try:
        if args.simulate:
            # Simulation mode
            cli.simulation_mode()
        elif args.query:
            # Single query mode
            cli.single_query_mode(args.query)
        else:
            # Interactive mode
            cli.interactive_mode()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

