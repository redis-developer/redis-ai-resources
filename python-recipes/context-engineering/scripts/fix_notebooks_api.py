#!/usr/bin/env python3
"""
Fix notebooks to use the actual MemoryAPIClient API correctly.

This script updates all notebooks to:
1. Import from agent_memory_client directly
2. Use MemoryClientConfig for initialization
3. Use correct method names and signatures
4. Handle tuple returns properly
"""

import json
import re
import sys
from pathlib import Path


def fix_imports(cell_source):
    """Fix imports to use agent_memory_client directly."""
    new_source = []
    for line in cell_source:
        # Replace redis_context_course imports with agent_memory_client
        if 'from redis_context_course import MemoryClient' in line:
            new_source.append('from agent_memory_client import MemoryAPIClient as MemoryClient, MemoryClientConfig\n')
        else:
            new_source.append(line)
    return new_source


def fix_initialization(cell_source):
    """Fix MemoryClient initialization to use MemoryClientConfig."""
    source_text = ''.join(cell_source)
    
    # Pattern: memory_client = MemoryClient(config=config)
    # This is already correct, just need to ensure config is created properly
    
    # Check if this cell creates a config
    if 'config = MemoryClientConfig(' in source_text:
        return cell_source  # Already correct
    
    # Check if this cell initializes memory_client without config
    if 'memory_client = MemoryClient(' in source_text and 'config=' not in source_text:
        # Need to add config creation
        new_source = []
        for line in cell_source:
            if 'memory_client = MemoryClient(' in line:
                # Add config creation before this line
                indent = line[:len(line) - len(line.lstrip())]
                new_source.append(f'{indent}import os\n')
                new_source.append(f'{indent}config = MemoryClientConfig(\n')
                new_source.append(f'{indent}    base_url=os.getenv("AGENT_MEMORY_URL", "http://localhost:8000")\n')
                new_source.append(f'{indent})\n')
                new_source.append(f'{indent}memory_client = MemoryClient(config=config)\n')
            elif ')' in line and 'memory_client' in ''.join(new_source[-5:]):
                # Skip closing paren of old initialization
                continue
            else:
                new_source.append(line)
        return new_source
    
    return cell_source


def fix_get_or_create_working_memory(cell_source):
    """Fix get_or_create_working_memory to unpack tuple."""
    new_source = []
    for i, line in enumerate(cell_source):
        if 'await memory_client.get_or_create_working_memory(' in line:
            # Check if already unpacking tuple
            if '_, working_memory =' in line or 'created, working_memory =' in line:
                new_source.append(line)
            else:
                # Need to unpack tuple
                line = line.replace(
                    'working_memory = await memory_client.get_or_create_working_memory(',
                    '_, working_memory = await memory_client.get_or_create_working_memory('
                )
                new_source.append(line)
        else:
            new_source.append(line)
    return new_source


def fix_search_memories(cell_source):
    """Fix search_memories to use search_long_term_memory."""
    new_source = []
    in_search_block = False

    for i, line in enumerate(cell_source):
        # Replace method name and parameter
        if 'memory_client.search_long_term_memory(' in line or 'memory_client.search_memories(' in line:
            line = line.replace('search_memories(', 'search_long_term_memory(')
            # Fix parameter name - handle both with and without await
            line = line.replace('query=', 'text=')
            # Store variable name
            if '=' in line and 'await' in line:
                var_name = line.split('=')[0].strip()
                in_search_block = True
            new_source.append(line)
        # Fix result access
        elif in_search_block and ('if ' in line or 'for ' in line):
            # Check if accessing memories directly
            if 'extracted_memories' in line or 'memories' in line:
                # Need to add .memories
                if 'for ' in line and ' in ' in line:
                    parts = line.split(' in ')
                    if len(parts) == 2 and '.memories' not in parts[1]:
                        var = parts[1].strip().rstrip(':,')
                        line = line.replace(f' in {var}', f' in {var}.memories')
                elif 'if ' in line:
                    if '.memories' not in line and 'extracted_memories' in line:
                        line = line.replace('extracted_memories:', 'extracted_memories.memories:')
            new_source.append(line)
            if ':' in line:
                in_search_block = False
        else:
            new_source.append(line)

    return new_source


def fix_save_working_memory(cell_source):
    """Fix save_working_memory calls - this method doesn't exist, need to use put_working_memory."""
    new_source = []
    skip_until_paren = False

    for line in cell_source:
        # Skip documentation references
        if 'save_working_memory()' in line and ('print(' in line or '"' in line or "'" in line):
            # This is just documentation, replace with put_working_memory
            line = line.replace('save_working_memory()', 'put_working_memory()')
            new_source.append(line)
        elif 'await memory_client.save_working_memory(' in line:
            # This is an actual call - need to convert to put_working_memory
            # For now, add a comment that this needs manual fixing
            indent = line[:len(line) - len(line.lstrip())]
            new_source.append(f'{indent}# TODO: save_working_memory needs to be replaced with put_working_memory\n')
            new_source.append(f'{indent}# which requires creating a WorkingMemory object\n')
            new_source.append(line)
            skip_until_paren = True
        elif skip_until_paren and ')' in line:
            new_source.append(line)
            skip_until_paren = False
        else:
            new_source.append(line)

    return new_source


def fix_notebook(notebook_path: Path) -> bool:
    """Fix a single notebook."""
    print(f"Processing: {notebook_path}")
    
    with open(notebook_path, 'r') as f:
        nb = json.load(f)
    
    modified = False
    
    for cell in nb['cells']:
        if cell['cell_type'] == 'code':
            original_source = cell['source'][:]
            
            # Apply fixes
            cell['source'] = fix_imports(cell['source'])
            cell['source'] = fix_initialization(cell['source'])
            cell['source'] = fix_get_or_create_working_memory(cell['source'])
            cell['source'] = fix_search_memories(cell['source'])
            cell['source'] = fix_save_working_memory(cell['source'])
            
            if cell['source'] != original_source:
                modified = True
    
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
    
    # Find all notebooks in section-3 and section-4
    patterns = [
        'section-3-memory/*.ipynb',
        'section-4-optimizations/*.ipynb'
    ]
    
    total_updated = 0
    
    for pattern in patterns:
        for notebook_path in notebooks_dir.glob(pattern):
            if fix_notebook(notebook_path):
                total_updated += 1
    
    print(f"\n✅ Updated {total_updated} notebooks")
    return 0


if __name__ == '__main__':
    sys.exit(main())

