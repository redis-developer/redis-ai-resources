#!/usr/bin/env python3
"""
Stage 3: Hybrid RAG Agent CLI

Interactive CLI demonstrating production-ready context engineering.
Shows hybrid context assembly with ~70% token reduction vs Stage 1.
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

from progressive_agents.stage3_hybrid.agent import HybridRAGAgent, HybridAgentConfig
from redis_context_course import redis_config

# Load environment variables
load_dotenv()

console = Console()


class Stage3CLI:
    """Interactive CLI for Stage 3 Hybrid RAG Agent."""
    
    def __init__(self, use_smart_selection: bool = True):
        self.config = HybridAgentConfig(use_smart_selection=use_smart_selection)
        self.agent = None
        
    async def initialize(self):
        """Initialize the agent and check connections."""
        console.print("[yellow]Initializing Stage 3: Hybrid RAG Agent...[/yellow]")
        
        # Check Redis connection
        if not redis_config.health_check():
            console.print("[red]❌ Redis connection failed. Please check your Redis server.[/red]")
            return False
        
        console.print("[green]✅ Redis connection successful[/green]")
        
        # Initialize agent
        try:
            self.agent = HybridRAGAgent(self.config)
            console.print("[green]✅ Hybrid RAG agent initialized[/green]")
            console.print(f"[cyan]Smart view selection: {'enabled' if self.config.use_smart_selection else 'disabled'}[/cyan]")
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
            "[bold blue]Stage 3: Hybrid RAG Agent[/bold blue]\n\n"
            "Production-ready context engineering with:\n"
            "• Structured catalog views (hierarchical organization)\n"
            "• Hybrid context assembly (overview + details)\n"
            "• Query-aware optimization (smart view selection)\n"
            "• Multi-strategy retrieval\n\n"
            "[green]✅ ~70% fewer tokens than Stage 1[/green]\n"
            "[green]✅ Better context organization[/green]\n"
            "[green]✅ Scalable to large catalogs[/green]\n\n"
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
                console.print("[dim]Building hybrid context...[/dim]")
                
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
            "• [cyan]metrics[/cyan] - Show token usage and views for last query\n"
            "• [cyan]compare[/cyan] - Compare all 3 stages\n"
            "• [cyan]help[/cyan] - Show this help message\n"
            "• [cyan]quit[/cyan] - Exit the chat\n\n"
            "[bold]Example Questions:[/bold]\n"
            "• What courses are available? (triggers catalog view)\n"
            "• What are the prerequisites for advanced ML? (triggers prereq view)\n"
            "• What beginner courses do you have? (triggers difficulty view)\n"
            "• Tell me about database courses (details only)",
            title="Help",
            border_style="cyan"
        )
        console.print(help_panel)
    
    async def _show_metrics(self, query: str):
        """Show metrics for the last query."""
        console.print("[dim]Calculating metrics...[/dim]")
        
        metrics = await self.agent.get_metrics(query)
        
        views_text = ", ".join(metrics['views_included']) if metrics['views_included'] else "details only"
        
        metrics_panel = Panel(
            f"[bold]Context Metrics:[/bold]\n\n"
            f"• Token count: [green]{metrics['token_count']:,}[/green]\n"
            f"• Character count: {metrics['character_count']:,}\n"
            f"• Format: {metrics['format']}\n"
            f"• Views included: {views_text}\n"
            f"• Smart selection: {'enabled' if metrics['smart_selection'] else 'disabled'}\n"
            f"• Est. cost per 1K queries: ${metrics['estimated_cost_per_1k_queries']}\n\n"
            f"[green]✅ ~70% fewer tokens than Stage 1![/green]",
            title="📊 Metrics",
            border_style="green"
        )
        console.print(metrics_panel)
    
    async def _show_comparison(self, query: str):
        """Show comparison across all stages."""
        console.print("[dim]Comparing all stages...[/dim]")
        
        comparison = await self.agent.compare_all_stages(query)
        
        # Create comparison table
        table = Table(title="All Stages Comparison")
        table.add_column("Stage", style="cyan")
        table.add_column("Format", style="white")
        table.add_column("Tokens", style="yellow")
        table.add_column("Cost/1K", style="green")
        table.add_column("vs Stage 1", style="magenta")
        
        table.add_row(
            "Stage 1 (Baseline)",
            comparison['stage1']['format'],
            f"{comparison['stage1']['tokens']:,}",
            f"${comparison['stage1']['cost_per_1k']:.2f}",
            "—"
        )
        
        table.add_row(
            "Stage 2 (Optimized)",
            comparison['stage2']['format'],
            f"{comparison['stage2']['tokens']:,}",
            f"${comparison['stage2']['cost_per_1k']:.2f}",
            comparison['stage2']['vs_stage1']
        )
        
        table.add_row(
            "Stage 3 (Hybrid)",
            comparison['stage3']['format'],
            f"{comparison['stage3']['tokens']:,}",
            f"${comparison['stage3']['cost_per_1k']:.2f}",
            comparison['stage3']['vs_stage1']
        )
        
        console.print(table)
        
        # Show savings summary
        stage1_tokens = comparison['stage1']['tokens']
        stage3_tokens = comparison['stage3']['tokens']
        savings = stage1_tokens - stage3_tokens
        
        savings_panel = Panel(
            f"[bold green]Total Savings (Stage 1 → Stage 3):[/bold green]\n\n"
            f"• Token reduction: {savings:,} tokens\n"
            f"• Percentage: {comparison['stage3']['vs_stage1']}\n"
            f"• Annual cost savings (1M queries): "
            f"${(comparison['stage1']['cost_per_1k'] - comparison['stage3']['cost_per_1k']) * 1000:.2f}\n\n"
            f"[dim]Stage 2 → Stage 3: {comparison['stage3']['vs_stage2']} additional reduction[/dim]",
            title="💰 Savings",
            border_style="green"
        )
        console.print(savings_panel)


@click.command()
@click.option('--model', default='gpt-4o-mini', help='OpenAI model to use')
@click.option('--max-results', default=5, help='Maximum courses to retrieve')
@click.option('--catalog-size', default=50, help='Number of courses for catalog view')
@click.option('--no-smart-selection', is_flag=True, help='Disable smart view selection')
def main(model: str, max_results: int, catalog_size: int, no_smart_selection: bool):
    """
    Stage 3: Hybrid RAG Agent CLI
    
    Production-ready context engineering with hybrid views and smart selection.
    """
    cli = Stage3CLI(use_smart_selection=not no_smart_selection)
    asyncio.run(cli.run_chat())


if __name__ == "__main__":
    main()

