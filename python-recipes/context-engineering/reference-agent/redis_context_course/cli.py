#!/usr/bin/env python3
"""
Command-line interface for the Redis University Class Agent.

This CLI provides an interactive way to chat with the agent and demonstrates
the context engineering concepts in practice.
"""

import asyncio
import os
import sys
from typing import Optional

import click
from dotenv import load_dotenv
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt

from .agent import ClassAgent
from .redis_config import redis_config

# Load environment variables
load_dotenv()

console = Console()


class ChatCLI:
    """Interactive chat CLI for the Class Agent."""

    def __init__(self, student_id: str):
        self.student_id = student_id
        self.agent = None
        self.thread_id = "cli_session"

    async def initialize(self):
        """Initialize the agent and check connections."""
        console.print("[yellow]Initializing Redis University Class Agent...[/yellow]")

        # Check Redis connection
        if not redis_config.health_check():
            console.print(
                "[red]❌ Redis connection failed. Please check your Redis server.[/red]"
            )
            return False

        console.print("[green]✅ Redis connection successful[/green]")

        # Initialize agent
        try:
            self.agent = ClassAgent(self.student_id)
            console.print("[green]✅ Agent initialized successfully[/green]")
            return True
        except Exception as e:
            console.print(f"[red]❌ Agent initialization failed: {e}[/red]")
            return False

    async def run_chat(self):
        """Run the interactive chat loop."""
        if not await self.initialize():
            return

        # Welcome message
        welcome_panel = Panel(
            "[bold blue]Welcome to Redis University Class Agent![/bold blue]\n\n"
            "I'm here to help you find courses, plan your academic journey, and provide "
            "personalized recommendations based on your interests and goals.\n\n"
            "[dim]Type 'help' for commands, 'quit' to exit[/dim]",
            title="🎓 Class Agent",
            border_style="blue",
        )
        console.print(welcome_panel)

        while True:
            try:
                # Get user input
                user_input = Prompt.ask("\n[bold cyan]You[/bold cyan]")

                if user_input.lower() in ["quit", "exit", "bye"]:
                    console.print("[yellow]Goodbye! Have a great day! 👋[/yellow]")
                    break

                if user_input.lower() == "help":
                    self.show_help()
                    continue

                if user_input.lower() == "clear":
                    console.clear()
                    continue

                # Show thinking indicator
                with console.status("[bold green]Agent is thinking...", spinner="dots"):
                    response = await self.agent.chat(user_input, self.thread_id)

                # Display agent response
                agent_panel = Panel(
                    Markdown(response), title="🤖 Class Agent", border_style="green"
                )
                console.print(agent_panel)

            except KeyboardInterrupt:
                console.print(
                    "\n[yellow]Chat interrupted. Type 'quit' to exit.[/yellow]"
                )
            except Exception as e:
                console.print(f"[red]Error: {e}[/red]")

    def show_help(self):
        """Show help information."""
        help_text = """
        **Available Commands:**
        
        • `help` - Show this help message
        • `clear` - Clear the screen
        • `quit` / `exit` / `bye` - Exit the chat
        
        **Example Queries:**
        
        • "I'm interested in computer science courses"
        • "What programming courses are available?"
        • "I want to learn about data science"
        • "Show me beginner-friendly courses"
        • "I prefer online courses"
        • "What are the prerequisites for CS101?"
        
        **Features:**
        
        • 🧠 **Memory**: I remember your preferences and goals
        • 🔍 **Search**: I can find courses based on your interests
        • 💡 **Recommendations**: I provide personalized course suggestions
        • 📚 **Context**: I understand your academic journey
        """

        help_panel = Panel(Markdown(help_text), title="📖 Help", border_style="yellow")
        console.print(help_panel)


@click.command()
@click.option("--student-id", default="demo_student", help="Student ID for the session")
@click.option("--redis-url", help="Redis connection URL")
def main(student_id: str, redis_url: Optional[str]):
    """Start the Redis University Class Agent CLI."""

    # Set Redis URL if provided
    if redis_url:
        os.environ["REDIS_URL"] = redis_url

    # Check for required environment variables
    if not os.getenv("OPENAI_API_KEY"):
        console.print("[red]❌ OPENAI_API_KEY environment variable is required[/red]")
        console.print("[yellow]Please set your OpenAI API key:[/yellow]")
        console.print("export OPENAI_API_KEY='your-api-key-here'")
        sys.exit(1)

    # Start the chat
    chat_cli = ChatCLI(student_id)

    try:
        asyncio.run(chat_cli.run_chat())
    except KeyboardInterrupt:
        console.print("\n[yellow]Goodbye! 👋[/yellow]")


if __name__ == "__main__":
    main()
