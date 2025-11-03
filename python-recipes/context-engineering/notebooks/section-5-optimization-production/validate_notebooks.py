#!/usr/bin/env python3
"""
Notebook Validation Script for Section 5
Validates notebooks by executing them and analyzing outputs
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple
import nbformat
from nbconvert.preprocessors import ExecutePreprocessor, CellExecutionError
from dotenv import load_dotenv

# Load .env file from context-engineering directory (two levels up)
env_path = Path(__file__).parent.parent.parent / '.env'
if env_path.exists():
    load_dotenv(env_path)
    print(f"🔧 Loaded environment from: {env_path}\n")

# ANSI color codes
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'  # No Color

def print_header(text: str):
    """Print a formatted header"""
    print("\n" + "=" * 80)
    print(text)
    print("=" * 80 + "\n")

def print_success(text: str):
    """Print success message"""
    print(f"{Colors.GREEN}✅ {text}{Colors.NC}")

def print_error(text: str):
    """Print error message"""
    print(f"{Colors.RED}❌ {text}{Colors.NC}")

def print_warning(text: str):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.NC}")

def print_info(text: str):
    """Print info message"""
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.NC}")

def check_environment() -> bool:
    """Check if required environment variables are set"""
    print_header("Step 1: Checking Environment Variables")
    
    required_vars = ["OPENAI_API_KEY"]
    optional_vars = {
        "REDIS_URL": "redis://localhost:6379",
        "AGENT_MEMORY_URL": "http://localhost:8000"
    }
    
    all_ok = True
    
    # Check required variables
    for var in required_vars:
        if os.getenv(var):
            print_success(f"{var} is set")
        else:
            print_error(f"{var} is NOT set")
            print(f"   Please set: export {var}='your-value-here'")
            all_ok = False
    
    # Check optional variables (use defaults)
    for var, default in optional_vars.items():
        value = os.getenv(var, default)
        print_success(f"{var}: {value}")
    
    return all_ok

def check_dependencies() -> bool:
    """Check if required Python packages are installed"""
    print_header("Step 2: Checking Python Dependencies")
    
    required_packages = [
        "langchain_openai",
        "langgraph",
        "redisvl",
        "agent_memory_client",
        "tiktoken",
        "nbformat",
        "nbconvert"
    ]
    
    all_ok = True
    
    for package in required_packages:
        try:
            __import__(package)
            print_success(package)
        except ImportError:
            print_error(f"{package} not installed")
            all_ok = False
    
    return all_ok

def execute_notebook(notebook_path: Path) -> Tuple[bool, str, Dict]:
    """
    Execute a notebook and return success status, error message, and stats
    
    Returns:
        (success, error_message, stats)
    """
    print_header(f"Executing: {notebook_path.name}")
    
    try:
        # Read notebook
        with open(notebook_path, 'r', encoding='utf-8') as f:
            nb = nbformat.read(f, as_version=4)
        
        # Count cells
        total_cells = len(nb.cells)
        code_cells = sum(1 for cell in nb.cells if cell.cell_type == 'code')
        
        print_info(f"Total cells: {total_cells} (Code: {code_cells}, Markdown: {total_cells - code_cells})")
        
        # Execute notebook
        ep = ExecutePreprocessor(timeout=600, kernel_name='python3')
        
        print_info("Executing cells...")
        ep.preprocess(nb, {'metadata': {'path': str(notebook_path.parent)}})
        
        # Count executed cells
        executed_cells = sum(1 for cell in nb.cells 
                           if cell.cell_type == 'code' and cell.get('execution_count'))
        
        stats = {
            'total_cells': total_cells,
            'code_cells': code_cells,
            'executed_cells': executed_cells,
            'markdown_cells': total_cells - code_cells
        }
        
        print_success(f"Executed {executed_cells}/{code_cells} code cells")
        
        return True, "", stats
        
    except CellExecutionError as e:
        # Extract cell index from error if available
        cell_idx = getattr(e, 'cell_index', 'unknown')
        error_msg = f"Error in cell {cell_idx}: {str(e)}"
        print_error(error_msg)

        # Try to extract more details
        if hasattr(e, 'traceback'):
            print("\nTraceback:")
            print('\n'.join(e.traceback))

        return False, error_msg, {}
        
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        print_error(error_msg)
        return False, error_msg, {}

def analyze_notebook_content(notebook_path: Path) -> Dict:
    """Analyze notebook content for validation"""
    print_info(f"Analyzing content of {notebook_path.name}...")
    
    with open(notebook_path, 'r', encoding='utf-8') as f:
        nb = nbformat.read(f, as_version=4)
    
    analysis = {
        'has_learning_objectives': False,
        'has_imports': False,
        'has_tests': False,
        'has_summary': False,
        'undefined_variables': []
    }
    
    # Check for key sections
    for cell in nb.cells:
        if cell.cell_type == 'markdown':
            content = cell.source.lower()
            if 'learning objective' in content:
                analysis['has_learning_objectives'] = True
            if 'summary' in content or 'takeaway' in content:
                analysis['has_summary'] = True
        
        elif cell.cell_type == 'code':
            content = cell.source
            if 'import' in content:
                analysis['has_imports'] = True
            if 'test' in content.lower() or 'await test_' in content:
                analysis['has_tests'] = True
    
    return analysis

def main():
    """Main validation function"""
    print_header("Section 5 Notebook Validation")
    
    # Check environment
    if not check_environment():
        print_error("Environment check failed. Please fix the issues above.")
        return 1
    
    # Check dependencies
    if not check_dependencies():
        print_error("Dependency check failed. Please install missing packages.")
        return 1
    
    # Define notebooks to validate
    notebooks_dir = Path(__file__).parent
    notebooks = [
        "01_measuring_optimizing_performance.ipynb",
        "02_scaling_semantic_tool_selection.ipynb",
        "03_production_readiness_quality_assurance.ipynb"
    ]
    
    results = []
    
    # Execute each notebook
    for notebook_name in notebooks:
        notebook_path = notebooks_dir / notebook_name
        
        if not notebook_path.exists():
            print_error(f"Notebook not found: {notebook_name}")
            results.append({
                'notebook': notebook_name,
                'success': False,
                'error': 'File not found'
            })
            continue
        
        # Analyze content first
        analysis = analyze_notebook_content(notebook_path)
        
        # Execute notebook
        success, error, stats = execute_notebook(notebook_path)
        
        results.append({
            'notebook': notebook_name,
            'success': success,
            'error': error,
            'stats': stats,
            'analysis': analysis
        })
        
        print()  # Blank line between notebooks
    
    # Print summary
    print_header("Validation Summary")
    
    passed = sum(1 for r in results if r['success'])
    failed = len(results) - passed
    
    print(f"Total notebooks: {len(results)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print()
    
    for result in results:
        if result['success']:
            print_success(f"{result['notebook']}")
            if result.get('stats'):
                stats = result['stats']
                print(f"   Cells: {stats['executed_cells']}/{stats['code_cells']} executed")
        else:
            print_error(f"{result['notebook']}")
            print(f"   Error: {result['error']}")
    
    print()
    
    # Content analysis summary
    print_header("Content Analysis")
    
    for result in results:
        if 'analysis' in result:
            print(f"\n{result['notebook']}:")
            analysis = result['analysis']
            
            if analysis['has_learning_objectives']:
                print_success("Has learning objectives")
            else:
                print_warning("Missing learning objectives")
            
            if analysis['has_imports']:
                print_success("Has imports section")
            else:
                print_warning("Missing imports section")
            
            if analysis['has_tests']:
                print_success("Has test cases")
            else:
                print_warning("Missing test cases")
            
            if analysis['has_summary']:
                print_success("Has summary/takeaways")
            else:
                print_warning("Missing summary/takeaways")
    
    print()
    
    # Return exit code
    if failed > 0:
        print_error(f"Validation FAILED: {failed} notebook(s) had errors")
        return 1
    else:
        print_success("All notebooks validated successfully!")
        return 0

if __name__ == "__main__":
    sys.exit(main())

