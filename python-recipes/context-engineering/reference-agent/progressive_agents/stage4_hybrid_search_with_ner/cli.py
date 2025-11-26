#!/usr/bin/env python3
"""
Interactive CLI for the Course Q&A Agent (Stage 3).

Usage:
    python cli.py                    # Interactive mode
    python cli.py "your question"    # Single query mode
    python cli.py --simulate         # Simulate with example queries
    python cli.py --no-cleanup       # Don't cleanup courses on exit
"""

import asyncio
import atexit
import os
import sys
from pathlib import Path

# Load environment variables from .env file
from dotenv import load_dotenv

# Load .env from reference-agent directory
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(env_path)

# Add agent module to path
sys.path.insert(0, str(Path(__file__).parent))

from agent import create_workflow, run_agent, setup_agent
from agent.setup import cleanup_courses


class CourseQACLI:
    """Interactive CLI for Course Q&A Agent."""

    def __init__(self, cleanup_on_exit: bool = False, debug: bool = False):
        self.agent = None
        self.course_manager = None
        self.cleanup_on_exit = cleanup_on_exit
        self.debug = debug

        # Register cleanup handler if requested
        if cleanup_on_exit:
            atexit.register(self._cleanup)

    def _cleanup(self):
        """Cleanup handler called on exit."""
        if self.course_manager and self.cleanup_on_exit:
            print("\n🧹 Cleaning up courses from Redis...")
            try:
                asyncio.run(cleanup_courses(self.course_manager))
                print("✅ Cleanup complete")
            except Exception as e:
                print(f"⚠️  Cleanup failed: {e}")

    async def initialize(self):
        """Initialize the agent and load course data."""
        print("=" * 80)
        print("Course Q&A Agent - Stage 3 (Full Agent without Memory)")
        print("=" * 80)
        print()

        # Check for required environment variables
        if not os.getenv("OPENAI_API_KEY"):
            print("❌ Error: OPENAI_API_KEY environment variable not set")
            print("   Please set it with: export OPENAI_API_KEY='your-key-here'")
            sys.exit(1)

        try:
            # Initialize the agent (will auto-load courses if needed)
            print("🔧 Initializing Course Q&A Agent...")
            print("📦 Loading courses into Redis (if not already loaded)...")
            self.course_manager, _ = await setup_agent(auto_load_courses=True)
            print()

            # Create the workflow
            print("🔧 Creating LangGraph workflow...")
            self.agent = create_workflow(self.course_manager)
            print("✅ Workflow created successfully")
            print()

            # Show cleanup status
            if self.cleanup_on_exit:
                print("🧹 Courses will be cleaned up on exit")
            else:
                print("💾 Courses will persist in Redis after exit")
            print()

        except Exception as e:
            print(f"\n❌ Initialization failed: {e}")
            if self.debug:
                import traceback

                traceback.print_exc()
            sys.exit(1)

    def ask_question(self, query: str, show_details: bool = True):
        """Ask a question and get a response."""
        print("=" * 80)
        print(f"❓ Question: {query}")
        print("=" * 80)
        print()

        # Run the agent
        result = run_agent(self.agent, query, enable_caching=False)

        # Print the response
        print("📝 Answer:")
        print("-" * 80)
        print(result["final_response"])
        print("-" * 80)
        print()

        if show_details:
            # Print metrics
            metrics = result["metrics"]
            print("📊 Performance:")
            print(f"   Total Time: {metrics['total_latency']:.2f}ms")
            print(f"   Sub-questions: {metrics['sub_question_count']}")
            print(f"   Questions Researched: {metrics['questions_researched']}")
            print(f"   Execution: {metrics['execution_path']}")
            print()

            # Print sub-questions if decomposed
            if len(result.get("sub_questions", [])) > 1:
                print("🧠 Sub-questions:")
                for i, sq in enumerate(result["sub_questions"], 1):
                    print(f"   {i}. {sq}")
                print()

        return result

    async def interactive_mode(self):
        """Run in interactive mode."""
        print("=" * 80)
        print("Interactive Mode - Ask questions about courses")
        print("Commands: 'quit' or 'exit' to stop, 'help' for help")
        print("=" * 80)
        print()

        while True:
            try:
                # Get user input
                query = input("❓ Your question: ").strip()

                if not query:
                    continue

                # Handle commands
                if query.lower() in ["quit", "exit", "q"]:
                    print("\n👋 Goodbye!")
                    break

                if query.lower() == "help":
                    self.show_help()
                    continue

                # Ask the question
                print()
                self.ask_question(query, show_details=True)

            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                if self.debug:
                    import traceback

                    traceback.print_exc()
                print()

    async def simulate_mode(self):
        """Run simulation with example queries."""
        print("=" * 80)
        print("Simulation Mode - Running example queries")
        print("=" * 80)
        print()

        example_queries = [
            "What machine learning courses are available for beginners?",
            "Tell me about database courses and their prerequisites",
            "What are the best courses for learning web development?",
            "I want to learn data science. What courses should I take?",
            "What advanced computer science courses are offered?",
        ]

        for i, query in enumerate(example_queries, 1):
            print(f"\n{'=' * 80}")
            print(f"Example {i}/{len(example_queries)}")
            print(f"{'=' * 80}\n")

            self.ask_question(query, show_details=True)

            # Pause between queries
            if i < len(example_queries):
                print("Press Enter to continue to next example...")
                input()

        print("=" * 80)
        print("✅ Simulation complete!")
        print("=" * 80)

    def show_help(self):
        """Show help information."""
        print()
        print("=" * 80)
        print("Help - Course Q&A Agent")
        print("=" * 80)
        print()
        print("This agent can answer questions about courses in the catalog.")
        print()
        print("Example questions:")
        print("  • What machine learning courses are available?")
        print("  • Tell me about database courses and their prerequisites")
        print("  • What courses should I take to learn web development?")
        print("  • What are the requirements for CS301?")
        print()
        print("Commands:")
        print("  • help  - Show this help message")
        print("  • quit  - Exit the program")
        print("  • exit  - Exit the program")
        print()
        print("=" * 80)
        print()


async def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Stage 3 Full Agent - Hierarchical Retrieval with Progressive Disclosure"
    )
    parser.add_argument(
        "query",
        nargs="?",
        help="Question to ask (if not provided, runs in interactive mode)",
    )
    parser.add_argument(
        "--simulate",
        action="store_true",
        help="Run simulation mode with example queries",
    )
    parser.add_argument(
        "--cleanup", action="store_true", help="Remove courses from Redis on exit"
    )
    parser.add_argument(
        "--no-cleanup",
        action="store_true",
        help="Keep courses in Redis after exit (default)",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Show detailed error messages and tracebacks",
    )

    args = parser.parse_args()

    # Determine cleanup behavior
    cleanup_on_exit = args.cleanup and not args.no_cleanup

    if args.simulate:
        # Simulation mode
        cli = CourseQACLI(cleanup_on_exit=cleanup_on_exit, debug=args.debug)
        await cli.initialize()
        await cli.simulate_mode()
    elif args.query:
        # Single query mode
        cli = CourseQACLI(cleanup_on_exit=cleanup_on_exit, debug=args.debug)
        await cli.initialize()
        cli.ask_question(args.query, show_details=True)
    else:
        # Interactive mode
        cli = CourseQACLI(cleanup_on_exit=cleanup_on_exit, debug=args.debug)
        await cli.initialize()
        await cli.interactive_mode()


if __name__ == "__main__":
    asyncio.run(main())
