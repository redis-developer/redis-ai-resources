#!/usr/bin/env python3
"""
Stage 4: Advanced Optimization Agent CLI

Interactive CLI demonstrating advanced optimization techniques:
- Prompt caching (commented out for now)
- Memory integration (optional)
- Catalog view caching
- Optimized context assembly
"""

import asyncio
import os
import sys
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from progressive_agents.stage4_advanced.agent import AdvancedOptimizationAgent
from redis_context_course import redis_config

# Load environment variables
load_dotenv()

console = Console()


class Stage4CLI:
    """Interactive CLI for Stage 4 Advanced Optimization Agent."""
    
    def __init__(self, use_memory: bool = False):
        self.use_memory = use_memory
        self.agent = None
        
    async def initialize(self):
        """Initialize the agent and check connections."""
        console.print("[yellow]Initializing Stage 4: Advanced Optimization Agent...[/yellow]")
        
        # Check Redis connection
        if not redis_config.health_check():
            console.print("[red]❌ Redis connection failed. Please check your Redis server.[/red]")
            return False
        
        console.print("[green]✅ Redis connection successful[/green]")
        
        # Check memory server if enabled
        if self.use_memory:
            memory_url = os.getenv("AGENT_MEMORY_URL", "http://localhost:8088")
            console.print(f"[yellow]Memory integration enabled: {memory_url}[/yellow]")
            console.print("[dim]Note: Make sure Agent Memory Server is running[/dim]")
        
        # Initialize agent
        try:
            self.agent = AdvancedOptimizationAgent(
                use_memory=self.use_memory
            )
            console.print("[green]✅ Advanced optimization agent initialized[/green]")
            console.print(f"[cyan]Memory: {'Enabled' if self.use_memory else 'Disabled'}[/cyan]")
            console.print(f"[cyan]Caching: {'Enabled' if self.agent.use_caching else 'Disabled (TODO)'}[/cyan]")
            return True
        except Exception as e:
            console.print(f"[red]❌ Agent initialization failed: {e}[/red]")
            import traceback
            traceback.print_exc()
            return False
    
    async def run_chat(self):
        """Run the interactive chat loop."""
        if not await self.initialize():
            return
        
        # Welcome message
        welcome_panel = Panel(
            "[bold blue]Stage 4: Advanced Optimization Agent (LangGraph)[/bold blue]\n\n"
            "This agent demonstrates advanced optimization techniques:\n"
            "• LangGraph StateGraph workflow\n"
            "• Catalog view caching (in-memory)\n"
            "• Optimized context assembly\n"
            "• Memory integration (optional)\n"
            "• Prompt caching support (TODO)\n\n"
            "[green]✅ Production-ready patterns for real-world applications[/green]\n\n"
            "[dim]Type 'metrics' to see optimization stats, 'help' for commands, 'quit' to exit[/dim]",
            title="🎓 Redis University Course Advisor",
            border_style="blue"
        )
        console.print(welcome_panel)
        
        last_query = None
        
        while True:
            # Get user input
            user_input = Prompt.ask("\n[bold cyan]You[/bold cyan]")
            
            if not user_input.strip():
                continue
            
            # Handle commands
            if user_input.lower() == "quit":
                console.print("[yellow]Goodbye! 👋[/yellow]")
                break
            
            elif user_input.lower() == "help":
                self.show_help()
                continue
            
            elif user_input.lower() == "metrics":
                if last_query:
                    await self.show_metrics(last_query)
                else:
                    console.print("[yellow]Ask a question first to see metrics[/yellow]")
                continue
            
            elif user_input.lower() == "compare":
                if last_query:
                    await self.show_comparison(last_query)
                else:
                    console.print("[yellow]Ask a question first to see comparison[/yellow]")
                continue
            
            # Process query
            last_query = user_input
            
            try:
                console.print("\n[dim]Thinking...[/dim]")
                response = await self.agent.chat(user_input)
                
                # Display response
                console.print(f"\n[bold green]Agent[/bold green]: {response}")
                
            except Exception as e:
                console.print(f"[red]Error: {e}[/red]")
                import traceback
                traceback.print_exc()
    
    def show_help(self):
        """Show available commands."""
        help_panel = Panel(
            """[bold]Available Commands:[/bold]

• [cyan]metrics[/cyan] - Show optimization metrics for last query
• [cyan]compare[/cyan] - Compare with Stage 1-3 (estimates)
• [cyan]help[/cyan] - Show this help message
• [cyan]quit[/cyan] - Exit the CLI

[bold]Features:[/bold]
• Catalog view caching (reused across queries)
• Optimized context assembly
• Memory integration (if enabled)
• Production-ready patterns
""",
            title="Help",
            border_style="cyan"
        )
        console.print(help_panel)
    
    async def show_metrics(self, query: str):
        """Show metrics for a query."""
        metrics = await self.agent.get_metrics(query)
        
        metrics_panel = Panel(
            f"[bold]Optimization Metrics[/bold]\n\n"
            f"Estimated tokens: [cyan]{metrics['estimated_tokens']:,}[/cyan]\n"
            f"Context length: [cyan]{metrics['context_length']:,}[/cyan] characters\n"
            f"Courses retrieved: [cyan]{metrics['num_courses']}[/cyan]\n"
            f"Catalog cache hit: [cyan]{'✅ Yes' if metrics['catalog_cache_hit'] else '❌ No (first query)'}[/cyan]\n"
            f"Format: [cyan]{metrics['format']}[/cyan]\n"
            f"Memory enabled: [cyan]{'✅ Yes' if metrics['memory_enabled'] else '❌ No'}[/cyan]\n"
            f"Prompt caching: [cyan]{'✅ Yes' if metrics['caching_enabled'] else '⏳ TODO'}[/cyan]\n\n"
            f"[green]✅ Optimized for production use[/green]",
            title="📊 Metrics",
            border_style="yellow"
        )
        console.print(metrics_panel)
    
    async def show_comparison(self, query: str):
        """Show comparison with other stages (estimated)."""
        metrics = await self.agent.get_metrics(query)
        
        # Create comparison table
        table = Table(title="Stage Comparison (Estimated)")
        table.add_column("Stage", style="cyan")
        table.add_column("Tokens", style="yellow")
        table.add_column("Format", style="green")
        table.add_column("Features", style="blue")
        
        # Estimates based on typical performance
        stage1_tokens = 2500
        stage2_tokens = 1200
        stage3_tokens = 800
        stage4_tokens = metrics['estimated_tokens']
        
        table.add_row(
            "Stage 1 (Baseline)",
            f"{stage1_tokens:,}",
            "Raw JSON",
            "Basic RAG"
        )
        table.add_row(
            "Stage 2 (Optimized)",
            f"{stage2_tokens:,}",
            "Natural text",
            "Context engineering"
        )
        table.add_row(
            "Stage 3 (Hybrid)",
            f"{stage3_tokens:,}",
            "Structured views",
            "Hybrid retrieval"
        )
        table.add_row(
            "Stage 4 (Advanced)",
            f"{stage4_tokens:,}",
            "Cached + hybrid",
            "Caching + memory",
            style="bold green"
        )
        
        console.print(table)
        
        # Show improvements
        improvement_vs_stage1 = ((stage1_tokens - stage4_tokens) / stage1_tokens * 100)
        improvement_vs_stage3 = ((stage3_tokens - stage4_tokens) / stage3_tokens * 100) if stage4_tokens < stage3_tokens else 0
        
        console.print(f"\n[green]✅ {improvement_vs_stage1:.1f}% improvement vs Stage 1[/green]")
        if improvement_vs_stage3 > 0:
            console.print(f"[green]✅ {improvement_vs_stage3:.1f}% improvement vs Stage 3[/green]")
        console.print(f"[cyan]💡 Catalog caching saves tokens on subsequent queries[/cyan]")


@click.command()
@click.option('--model', default='gpt-4o-mini', help='OpenAI model to use')
@click.option('--memory/--no-memory', default=False, help='Enable memory integration')
def main(model: str, memory: bool):
    """
    Stage 4: Advanced Optimization Agent CLI (LangGraph Version)
    
    A production-ready course advisor with advanced optimizations.
    Uses LangGraph StateGraph for workflow orchestration.
    """
    cli = Stage4CLI(use_memory=memory)
    asyncio.run(cli.run_chat())


if __name__ == "__main__":
    main()

