#!/usr/bin/env python3
"""
Stage 2: Context-Engineered Agent CLI

Interactive CLI demonstrating context engineering optimizations.
Shows ~50% token reduction vs Stage 1 baseline.
"""

import asyncio
import sys
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.markdown import Markdown
from rich.table import Table
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from progressive_agents.stage2_optimized.agent import ContextEngineeredAgent
from redis_context_course import redis_config

# Load environment variables
load_dotenv()

console = Console()


class Stage2CLI:
    """Interactive CLI for Stage 2 Context-Engineered Agent."""
    
    def __init__(self, optimization_level: str = "standard"):
        self.config = OptimizedAgentConfig(optimization_level=optimization_level)
        self.agent = None
        
    async def initialize(self):
        """Initialize the agent and check connections."""
        console.print("[yellow]Initializing Stage 2: Context-Engineered Agent...[/yellow]")
        
        # Check Redis connection
        if not redis_config.health_check():
            console.print("[red]❌ Redis connection failed. Please check your Redis server.[/red]")
            return False
        
        console.print("[green]✅ Redis connection successful[/green]")
        
        # Initialize agent
        try:
            self.agent = ContextEngineeredAgent(self.config)
            console.print("[green]✅ Context-engineered agent initialized[/green]")
            console.print(f"[cyan]Optimization level: {self.config.optimization_level}[/cyan]")
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
            "[bold blue]Stage 2: Context-Engineered Agent[/bold blue]\n\n"
            "This agent applies context engineering techniques:\n"
            "• Context cleaning (remove unnecessary fields)\n"
            "• Natural text transformation (JSON → text)\n"
            "• Token optimization (~50% reduction)\n\n"
            "[green]✅ ~50% fewer tokens than Stage 1[/green]\n"
            "[green]✅ Better LLM comprehension[/green]\n"
            "[green]✅ Lower costs[/green]\n\n"
            "[dim]Commands: 'metrics', 'compare', 'help', 'quit'[/dim]",
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
                
                if user_input.lower() == 'compare' and last_query:
                    await self._show_comparison(last_query)
                    continue
                
                # Process query
                console.print("[dim]Searching and optimizing context...[/dim]")
                
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
            "• [cyan]compare[/cyan] - Compare with Stage 1 baseline\n"
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
        context = self.agent.format_context(courses)
        metrics = self.agent.get_metrics(context)
        
        metrics_panel = Panel(
            f"[bold]Context Metrics:[/bold]\n\n"
            f"• Token count: [green]{metrics['token_count']:,}[/green]\n"
            f"• Character count: {metrics['character_count']:,}\n"
            f"• Format: {metrics['format']}\n"
            f"• Optimization: {metrics['optimization_level']}\n"
            f"• Courses retrieved: {len(courses)}\n"
            f"• Est. cost per 1K queries: ${metrics['estimated_cost_per_1k_queries']}\n\n"
            f"[green]✅ ~50% fewer tokens than Stage 1![/green]",
            title="📊 Metrics",
            border_style="green"
        )
        console.print(metrics_panel)
    
    async def _show_comparison(self, query: str):
        """Show comparison with Stage 1 baseline."""
        console.print("[dim]Comparing with baseline...[/dim]")
        
        comparison = await self.agent.compare_with_baseline(query)
        
        # Create comparison table
        table = Table(title="Stage 1 vs Stage 2 Comparison")
        table.add_column("Metric", style="cyan")
        table.add_column("Stage 1 (Baseline)", style="red")
        table.add_column("Stage 2 (Optimized)", style="green")
        table.add_column("Improvement", style="yellow")
        
        table.add_row(
            "Token Count",
            f"{comparison['baseline_tokens']:,}",
            f"{comparison['optimized_tokens']:,}",
            f"-{comparison['token_savings']:,}"
        )
        
        baseline_cost = comparison['all_formats']['raw_json']['tokens'] * 0.150 / 1000
        optimized_cost = comparison['optimized_tokens'] * 0.150 / 1000
        
        table.add_row(
            "Cost per Query",
            f"${baseline_cost:.4f}",
            f"${optimized_cost:.4f}",
            f"-{comparison['reduction_percentage']}"
        )
        
        table.add_row(
            "Format",
            "Raw JSON",
            "Natural Text",
            "Better LLM parsing"
        )
        
        console.print(table)
        
        # Show all format options
        formats_panel = Panel(
            "[bold]All Format Options:[/bold]\n\n"
            + "\n".join([
                f"• {name}: {data['tokens']:,} tokens ({data['reduction_vs_baseline']} reduction)"
                for name, data in comparison['all_formats'].items()
            ]),
            title="Format Comparison",
            border_style="cyan"
        )
        console.print(formats_panel)


@click.command()
@click.option('--model', default='gpt-4o-mini', help='OpenAI model to use')
@click.option('--max-results', default=5, help='Maximum courses to retrieve')
@click.option('--optimization', 
              type=click.Choice(['standard', 'aggressive']), 
              default='standard',
              help='Optimization level (standard=natural text, aggressive=compact)')
def main(model: str, max_results: int, optimization: str):
    """
    Stage 2: Context-Engineered Agent CLI
    
    Demonstrates context engineering techniques with ~50% token reduction.
    """
    cli = Stage2CLI(optimization_level=optimization)
    asyncio.run(cli.run_chat())


if __name__ == "__main__":
    main()

