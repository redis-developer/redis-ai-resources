#!/usr/bin/env python3
"""
Update notebooks to use MemoryAPIClient directly instead of wrapper.
"""

import json
import sys
from pathlib import Path


def update_notebook(notebook_path: Path) -> bool:
    """Update a single notebook to use MemoryAPIClient directly."""
    print(f"Processing: {notebook_path}")
    
    with open(notebook_path, 'r') as f:
        nb = json.load(f)
    
    modified = False
    
    for cell in nb['cells']:
        if cell['cell_type'] == 'code':
            source_text = ''.join(cell['source'])
            
            # Check if this cell imports MemoryClient
            if 'from redis_context_course import MemoryClient' in source_text:
                new_source = []
                for line in cell['source']:
                    if 'from redis_context_course import MemoryClient' in line:
                        # Update import to include MemoryClientConfig
                        new_source.append('from redis_context_course import MemoryClient, MemoryClientConfig\n')
                        modified = True
                    else:
                        new_source.append(line)
                
                if modified:
                    cell['source'] = new_source
            
            # Check if this cell initializes MemoryClient with old API
            if 'memory_client = MemoryClient(' in source_text and 'user_id=' in source_text:
                new_source = []
                in_memory_client_init = False
                indent = ''
                user_id_var = None
                namespace_val = 'redis_university'
                
                for i, line in enumerate(cell['source']):
                    if 'memory_client = MemoryClient(' in line:
                        in_memory_client_init = True
                        # Extract indentation
                        indent = line[:len(line) - len(line.lstrip())]
                        # Start building new initialization
                        new_source.append(f'{indent}# Initialize memory client with proper config\n')
                        new_source.append(f'{indent}import os\n')
                        new_source.append(f'{indent}config = MemoryClientConfig(\n')
                        new_source.append(f'{indent}    base_url=os.getenv("AGENT_MEMORY_URL", "http://localhost:8000"),\n')
                        new_source.append(f'{indent}    default_namespace="redis_university"\n')
                        new_source.append(f'{indent})\n')
                        new_source.append(f'{indent}memory_client = MemoryClient(config=config)\n')
                        modified = True
                    elif in_memory_client_init:
                        # Skip lines until we find the closing parenthesis
                        if ')' in line and not line.strip().startswith('#'):
                            in_memory_client_init = False
                        # Skip this line (it's part of old init)
                        continue
                    else:
                        new_source.append(line)
                
                if modified:
                    cell['source'] = new_source
    
    if modified:
        with open(notebook_path, 'w') as f:
            json.dump(nb, f, indent=2, ensure_ascii=False)
            f.write('\n')
        print(f"  ✅ Updated {notebook_path.name}")
        return True
    else:
        print(f"  ⏭️  No changes needed for {notebook_path.name}")
        return False


def main():
    notebooks_dir = Path(__file__).parent.parent / 'notebooks'
    
    # Find all notebooks that use MemoryClient
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

