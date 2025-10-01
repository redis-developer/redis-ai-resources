#!/usr/bin/env python3
"""
Update notebooks to use get_or_create_working_memory instead of get_working_memory.

This ensures notebooks work correctly even when working memory doesn't exist yet.
"""

import json
import sys
from pathlib import Path


def update_notebook(notebook_path: Path) -> bool:
    """Update a single notebook to use get_or_create_working_memory."""
    print(f"Processing: {notebook_path}")
    
    with open(notebook_path, 'r') as f:
        nb = json.load(f)
    
    modified = False
    
    for cell in nb['cells']:
        if cell['cell_type'] == 'code':
            new_source = []
            for line in cell['source']:
                # Replace get_working_memory with get_or_create_working_memory
                # but only in actual code calls, not in comments or strings
                if 'memory_client.get_working_memory(' in line and not line.strip().startswith('#'):
                    # Don't replace if it's in a print statement or comment
                    if 'print(' not in line or 'get_or_create' in line:
                        line = line.replace('.get_working_memory(', '.get_or_create_working_memory(')
                        modified = True
                new_source.append(line)
            cell['source'] = new_source
    
    if modified:
        with open(notebook_path, 'w') as f:
            json.dump(nb, f, indent=2, ensure_ascii=False)
            f.write('\n')  # Add trailing newline
        print(f"  ✅ Updated {notebook_path.name}")
        return True
    else:
        print(f"  ⏭️  No changes needed for {notebook_path.name}")
        return False


def main():
    notebooks_dir = Path(__file__).parent.parent / 'notebooks'
    
    # Find all notebooks in section-3 and section-4
    patterns = [
        'section-3-memory/*.ipynb',
        'section-4-optimizations/*.ipynb'
    ]
    
    total_updated = 0
    
    for pattern in patterns:
        for notebook_path in notebooks_dir.glob(pattern):
            if update_notebook(notebook_path):
                total_updated += 1
    
    print(f"\n✅ Updated {total_updated} notebooks")
    return 0


if __name__ == '__main__':
    sys.exit(main())

