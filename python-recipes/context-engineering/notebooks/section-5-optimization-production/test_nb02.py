#!/usr/bin/env python3
"""Quick test of notebook 02"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import nbformat
from nbconvert.preprocessors import ExecutePreprocessor

# Load .env
env_path = Path(__file__).parent.parent.parent / '.env'
if env_path.exists():
    load_dotenv(env_path)
    print(f"✅ Loaded environment from: {env_path}")

# Check API key
if not os.getenv("OPENAI_API_KEY"):
    print("❌ OPENAI_API_KEY not set")
    sys.exit(1)

print(f"✅ OPENAI_API_KEY is set")
print(f"✅ REDIS_URL: {os.getenv('REDIS_URL', 'redis://localhost:6379')}")
print(f"✅ AGENT_MEMORY_URL: {os.getenv('AGENT_MEMORY_URL', 'http://localhost:8000')}")

# Execute notebook 02
notebook_path = Path(__file__).parent / "02_scaling_semantic_tool_selection.ipynb"

print(f"\n📓 Executing: {notebook_path.name}")

try:
    with open(notebook_path, 'r', encoding='utf-8') as f:
        nb = nbformat.read(f, as_version=4)
    
    total_cells = len(nb.cells)
    code_cells = sum(1 for cell in nb.cells if cell.cell_type == 'code')
    
    print(f"   Total cells: {total_cells} (Code: {code_cells}, Markdown: {total_cells - code_cells})")
    print(f"   Executing cells...")
    
    ep = ExecutePreprocessor(timeout=600, kernel_name='python3')
    ep.preprocess(nb, {'metadata': {'path': str(notebook_path.parent)}})
    
    executed_cells = sum(1 for cell in nb.cells 
                       if cell.cell_type == 'code' and cell.get('execution_count'))
    
    print(f"\n✅ SUCCESS: Executed {executed_cells}/{code_cells} code cells")
    
except Exception as e:
    print(f"\n❌ FAILED: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

