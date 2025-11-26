#!/usr/bin/env python3
"""
Stage 1: Baseline RAG Agent CLI

Simple command-line interface for testing the baseline agent.
Demonstrates basic Q&A without optimization or memory.
"""

import asyncio
import sys
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.markdown import Markdown
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from progressive_agents.stage1_baseline.agent import BaselineRAGAgent
from redis_context_course import redis_config

# Load environment variables
load_dotenv()

console = Console()


class Stage1CLI:
    """Interactive CLI for Stage 1 Baseline Agent."""
    
    def __init__(self):
        self.agent = None
        
    async def initialize(self):
        """Initialize the agent and check connections."""
        console.print("[yellow]Initializing Stage 1: Baseline RAG Agent...[/yellow]")
        
        # Check Redis connection
        if not redis_config.health_check():
            console.print("[red]❌ Redis connection failed. Please check your Redis server.[/red]")
            return False
        
        console.print("[green]✅ Redis connection successful[/green]")
        
        # Initialize agent
        try:
            self.agent = BaselineRAGAgent()
            console.print("[green]✅ Baseline agent initialized[/green]")
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
            "[bold blue]Stage 1: Baseline RAG Agent (LangGraph)[/bold blue]\n\n"
            "This is a simple RAG implementation with:\n"
            "• LangGraph StateGraph workflow\n"
            "• Semantic search retrieval\n"
            "• Raw JSON context (inefficient)\n"
            "• No optimization\n"
            "• No memory\n\n"
            "[yellow]⚠️  This agent uses 2-3x more tokens than optimized versions[/yellow]\n\n"
            "[dim]Type 'metrics' to see token usage, 'quit' to exit[/dim]",
            title="🎓 Redis University Course Advisor",
            border_style="blue"
        )
        console.print(welcome_panel)
        
        last_query = None
        
        while True:
            try:
                # Get user input
                user_input = Prompt.ask("\n[bold cyan]You[/bold cyan]")
                
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    console.print("[yellow]Goodbye! 👋[/yellow]")
                    break
                
                if user_input.lower() == 'help':
                    self._show_help()
                    continue
                
                if user_input.lower() == 'metrics' and last_query:
                    await self._show_metrics(last_query)
                    continue
                
                # Process query
                console.print("[dim]Searching courses...[/dim]")
                
                response = await self.agent.chat(user_input)
                last_query = user_input
                
                # Display response
                console.print("\n[bold green]Agent[/bold green]")
                console.print(Markdown(response))
                
            except KeyboardInterrupt:
                console.print("\n[yellow]Interrupted. Type 'quit' to exit.[/yellow]")
            except Exception as e:
                console.print(f"[red]Error: {e}[/red]")
    
    def _show_help(self):
        """Show help message."""
        help_panel = Panel(
            "[bold]Available Commands:[/bold]\n\n"
            "• Ask any question about courses\n"
            "• [cyan]metrics[/cyan] - Show token usage for last query\n"
            "• [cyan]help[/cyan] - Show this help message\n"
            "• [cyan]quit[/cyan] - Exit the chat\n\n"
            "[bold]Example Questions:[/bold]\n"
            "• What machine learning courses are available?\n"
            "• Tell me about database courses\n"
            "• What are the prerequisites for advanced courses?",
            title="Help",
            border_style="cyan"
        )
        console.print(help_panel)
    
    async def _show_metrics(self, query: str):
        """Show metrics for the last query."""
        console.print("[dim]Calculating metrics...[/dim]")
        
        # Retrieve and format context
        courses = await self.agent.retrieve_courses(query)
        context = self.agent.format_context_as_json(courses)
        metrics = self.agent.get_metrics(context)
        
        metrics_panel = Panel(
            f"[bold]Context Metrics:[/bold]\n\n"
            f"• Token count: [yellow]{metrics['token_count']:,}[/yellow]\n"
            f"• Character count: {metrics['character_count']:,}\n"
            f"• Format: {metrics['format']}\n"
            f"• Optimization: {metrics['optimization_level']}\n"
            f"• Courses retrieved: {len(courses)}\n\n"
            f"[yellow]⚠️  This is 2-3x higher than optimized formats![/yellow]\n"
            f"[dim]See Stage 2 for optimization techniques[/dim]",
            title="📊 Metrics",
            border_style="yellow"
        )
        console.print(metrics_panel)


@click.command()
@click.option('--model', default='gpt-4o-mini', help='OpenAI model to use')
def main(model: str):
    """
    Stage 1: Baseline RAG Agent CLI (LangGraph Version)

    A simple course advisor demonstrating basic RAG without optimization.
    Uses LangGraph StateGraph for workflow orchestration.
    """
    # Note: max_results is now hardcoded in the agent (5 courses)
    # The LangGraph version simplifies configuration

    cli = Stage1CLI()
    asyncio.run(cli.run_chat())


if __name__ == "__main__":
    main()

