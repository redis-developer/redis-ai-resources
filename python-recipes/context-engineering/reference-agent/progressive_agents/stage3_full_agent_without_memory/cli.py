#!/usr/bin/env python3
"""
Interactive CLI for the Course Q&A Agent (Stage 3).

This CLI provides an interactive REPL for asking questions about courses.
It loads all course data on startup and maintains the agent session.

Usage:
    python cli.py
    
Commands:
    - Type your question and press Enter
    - 'metrics' - Show performance metrics for last query
    - 'help' - Show available commands
    - 'clear' - Clear the screen
    - 'exit' or 'quit' - Exit the CLI
"""

import asyncio
import os
import sys
from pathlib import Path

# Add parent directory to path to import agent module
sys.path.insert(0, str(Path(__file__).parent))

from agent import setup_agent, create_workflow, run_agent


class CourseQACLI:
    """Interactive CLI for the Course Q&A Agent."""
    
    def __init__(self):
        self.agent = None
        self.course_manager = None
        self.last_result = None
        
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
            return False
        
        try:
            # Initialize the agent
            print("🔧 Initializing Course Q&A Agent...")
            self.course_manager, _ = await setup_agent()
            print()
            
            # Create the workflow
            print("🔧 Creating LangGraph workflow...")
            self.agent = create_workflow(self.course_manager)
            print("✅ Workflow created successfully")
            print()
            
            # Load and display course count
            all_courses = await self.course_manager.get_all_courses()
            print(f"📚 Loaded {len(all_courses)} courses from the catalog")
            print()
            
            return True
            
        except Exception as e:
            print(f"\n❌ Initialization failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def show_help(self):
        """Display help information."""
        print("\n" + "=" * 80)
        print("Available Commands:")
        print("=" * 80)
        print("  <question>  - Ask a question about courses")
        print("  metrics     - Show performance metrics for the last query")
        print("  help        - Show this help message")
        print("  clear       - Clear the screen")
        print("  exit/quit   - Exit the CLI")
        print("=" * 80)
        print("\nExample questions:")
        print("  - What machine learning courses are available?")
        print("  - Tell me about database courses and their prerequisites")
        print("  - What are the best courses for learning web development?")
        print("=" * 80 + "\n")
    
    def show_metrics(self):
        """Display metrics from the last query."""
        if not self.last_result:
            print("\n❌ No query has been run yet\n")
            return
        
        metrics = self.last_result.get("metrics", {})
        llm_calls = self.last_result.get("llm_calls", {})
        
        print("\n" + "=" * 80)
        print("📊 Performance Metrics (Last Query)")
        print("=" * 80)
        print(f"Total Latency:        {metrics.get('total_latency', 0):.2f}ms")
        print(f"Decomposition:        {metrics.get('decomposition_latency', 0):.2f}ms")
        print(f"Cache Check:          {metrics.get('cache_latency', 0):.2f}ms")
        print(f"Research:             {metrics.get('research_latency', 0):.2f}ms")
        print(f"Synthesis:            {metrics.get('synthesis_latency', 0):.2f}ms")
        print(f"Cache Hit Rate:       {metrics.get('cache_hit_rate', 0):.1f}%")
        print(f"Sub-questions:        {metrics.get('sub_question_count', 0)}")
        print(f"Questions Researched: {metrics.get('questions_researched', 0)}")
        print(f"Execution Path:       {metrics.get('execution_path', 'N/A')}")
        
        if llm_calls:
            print("\n🤖 LLM Usage:")
            for llm_type, count in llm_calls.items():
                print(f"  {llm_type}: {count} calls")
        
        # Show sub-questions if decomposed
        sub_questions = self.last_result.get("sub_questions", [])
        if len(sub_questions) > 1:
            print("\n🧠 Sub-questions:")
            for i, sq in enumerate(sub_questions, 1):
                print(f"  {i}. {sq}")
        
        print("=" * 80 + "\n")
    
    def clear_screen(self):
        """Clear the terminal screen."""
        os.system('clear' if os.name != 'nt' else 'cls')
    
    async def process_query(self, query: str):
        """Process a user query and display the response."""
        print("\n🔍 Processing query...")
        print()
        
        try:
            # Run the agent
            result = run_agent(self.agent, query, enable_caching=False)
            self.last_result = result
            
            # Display the response
            print("=" * 80)
            print("📝 Response:")
            print("=" * 80)
            print(result["final_response"])
            print("=" * 80)
            print()
            
            # Show quick metrics summary
            metrics = result["metrics"]
            print(f"⏱️  Completed in {metrics['total_latency']:.2f}ms")
            print(f"📊 {metrics['sub_question_count']} sub-questions, {metrics['questions_researched']} researched")
            print(f"💡 Type 'metrics' to see detailed performance metrics")
            print()
            
        except Exception as e:
            print(f"\n❌ Error processing query: {e}")
            import traceback
            traceback.print_exc()
            print()
    
    async def run(self):
        """Run the interactive CLI loop."""
        # Initialize
        if not await self.initialize():
            return
        
        # Show welcome message
        print("=" * 80)
        print("🎓 Welcome to the Course Q&A Agent!")
        print("=" * 80)
        print("Ask me anything about courses. Type 'help' for commands, 'exit' to quit.")
        print("=" * 80)
        print()
        
        # Main loop
        while True:
            try:
                # Get user input
                query = input("💬 You: ").strip()
                
                # Handle empty input
                if not query:
                    continue
                
                # Handle commands
                if query.lower() in ['exit', 'quit']:
                    print("\n👋 Goodbye!\n")
                    break
                elif query.lower() == 'help':
                    self.show_help()
                elif query.lower() == 'metrics':
                    self.show_metrics()
                elif query.lower() == 'clear':
                    self.clear_screen()
                else:
                    # Process as a course query
                    await self.process_query(query)
                    
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!\n")
                break
            except EOFError:
                print("\n\n👋 Goodbye!\n")
                break
            except Exception as e:
                print(f"\n❌ Unexpected error: {e}\n")
                import traceback
                traceback.print_exc()


async def main():
    """Main entry point for the CLI."""
    cli = CourseQACLI()
    await cli.run()


if __name__ == "__main__":
    asyncio.run(main())

