#!/usr/bin/env python3
"""
Fix all query= to text= in search_long_term_memory calls across all notebooks.
Also fix missing imports.
"""

import json
import glob
from pathlib import Path


def fix_notebook(notebook_path):
    """Fix a single notebook."""
    with open(notebook_path, 'r') as f:
        nb = json.load(f)
    
    modified = False
    for cell in nb['cells']:
        if cell['cell_type'] == 'code':
            new_source = []
            for line in cell['source']:
                original = line
                # Fix query= to text= in search_long_term_memory calls
                if 'search_long_term_memory' in line or (len(new_source) > 0 and 'search_long_term_memory' in ''.join(new_source[-3:])):
                    line = line.replace('query=', 'text=')
                
                # Fix missing imports
                if 'from agent_memory_client import WorkingMemory' in line:
                    line = line.replace('from agent_memory_client import WorkingMemory', 'from agent_memory_client.models import WorkingMemory')
                if 'from agent_memory_client import MemoryMessage' in line:
                    line = line.replace('from agent_memory_client import MemoryMessage', 'from agent_memory_client.models import MemoryMessage')
                
                new_source.append(line)
                if line != original:
                    modified = True
            cell['source'] = new_source
    
    if modified:
        with open(notebook_path, 'w') as f:
            json.dump(nb, f, indent=2, ensure_ascii=False)
            f.write('\n')
        return True
    return False


def main():
    notebooks_dir = Path(__file__).parent.parent / 'notebooks'
    
    fixed_count = 0
    for notebook_path in notebooks_dir.glob('**/*.ipynb'):
        if '.ipynb_checkpoints' in str(notebook_path):
            continue
        
        if fix_notebook(notebook_path):
            print(f"Fixed: {notebook_path.relative_to(notebooks_dir)}")
            fixed_count += 1
    
    print(f"\nFixed {fixed_count} notebooks")


if __name__ == '__main__':
    main()

