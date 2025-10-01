#!/usr/bin/env python3
"""
Fix syntax errors and API usage issues in notebooks.
"""

import json
import re
from pathlib import Path


def fix_04_memory_tools(notebook_path):
    """Fix 04_memory_tools.ipynb issues."""
    with open(notebook_path, 'r') as f:
        nb = json.load(f)
    
    modified = False
    for cell in nb['cells']:
        if cell['cell_type'] == 'code':
            source = ''.join(cell['source'])
            
            # Fix missing closing bracket in create_long_term_memory call
            if 'await memory_client.create_long_term_memory([ClientMemoryRecord(' in source:
                new_source = []
                in_create_call = False
                bracket_count = 0
                
                for line in cell['source']:
                    if 'await memory_client.create_long_term_memory([ClientMemoryRecord(' in line:
                        in_create_call = True
                        bracket_count = line.count('[') - line.count(']')
                    elif in_create_call:
                        bracket_count += line.count('[') - line.count(']')
                        bracket_count += line.count('(') - line.count(')')
                    
                    # If we see the closing paren for ClientMemoryRecord but no closing bracket
                    if in_create_call and '))' in line and bracket_count > 0:
                        # Add the missing closing bracket
                        line = line.replace('))', ')])')
                        in_create_call = False
                        modified = True
                    
                    new_source.append(line)
                
                cell['source'] = new_source
    
    if modified:
        with open(notebook_path, 'w') as f:
            json.dump(nb, f, indent=2, ensure_ascii=False)
            f.write('\n')
        return True
    return False


def fix_03_memory_integration(notebook_path):
    """Fix 03_memory_integration.ipynb issues."""
    with open(notebook_path, 'r') as f:
        nb = json.load(f)
    
    modified = False
    for cell in nb['cells']:
        if cell['cell_type'] == 'code':
            source = ''.join(cell['source'])
            
            # Fix 1: Add missing user_id to get_or_create_working_memory calls
            if 'get_or_create_working_memory(' in source and 'user_id=' not in source:
                new_source = []
                for i, line in enumerate(cell['source']):
                    new_source.append(line)
                    # Add user_id after session_id
                    if 'session_id=' in line and i + 1 < len(cell['source']) and 'model_name=' in cell['source'][i + 1]:
                        indent = len(line) - len(line.lstrip())
                        new_source.append(' ' * indent + 'user_id="demo_user",\n')
                        modified = True
                cell['source'] = new_source
                source = ''.join(cell['source'])
            
            # Fix 2: Fix incomplete list comprehension
            if 'memory_messages = [MemoryMessage(**msg) for msg in []' in source and not 'memory_messages = [MemoryMessage(**msg) for msg in []]' in source:
                new_source = []
                for line in cell['source']:
                    if 'memory_messages = [MemoryMessage(**msg) for msg in []' in line and line.strip().endswith('[]'):
                        # This line is incomplete, should be empty list
                        line = line.replace('for msg in []', 'for msg in []]')
                        modified = True
                    new_source.append(line)
                cell['source'] = new_source
                source = ''.join(cell['source'])
            
            # Fix 3: Fix iteration over search results - need .memories
            if 'for i, memory in enumerate(memories' in source and 'enumerate(memories.memories' not in source:
                new_source = []
                for line in cell['source']:
                    if 'for i, memory in enumerate(memories' in line and '.memories' not in line:
                        line = line.replace('enumerate(memories', 'enumerate(memories.memories')
                        modified = True
                    elif 'for memory in long_term_memories:' in line:
                        line = line.replace('for memory in long_term_memories:', 'for memory in long_term_memories.memories:')
                        modified = True
                    new_source.append(line)
                cell['source'] = new_source
                source = ''.join(cell['source'])
            
            # Fix 4: Fix filtering - all_memories is a result object
            if '[m for m in all_memories if m.memory_type' in source:
                new_source = []
                for line in cell['source']:
                    if '[m for m in all_memories if m.memory_type' in line:
                        line = line.replace('[m for m in all_memories if m.memory_type', '[m for m in all_memories.memories if m.memory_type')
                        modified = True
                    new_source.append(line)
                cell['source'] = new_source
    
    if modified:
        with open(notebook_path, 'w') as f:
            json.dump(nb, f, indent=2, ensure_ascii=False)
            f.write('\n')
        return True
    return False


def main():
    notebooks_dir = Path(__file__).parent.parent / 'notebooks'
    
    # Fix specific notebooks
    fixed = []
    
    nb_path = notebooks_dir / 'section-3-memory' / '04_memory_tools.ipynb'
    if nb_path.exists() and fix_04_memory_tools(nb_path):
        fixed.append(str(nb_path.relative_to(notebooks_dir)))
    
    nb_path = notebooks_dir / 'section-3-memory' / '03_memory_integration.ipynb'
    if nb_path.exists() and fix_03_memory_integration(nb_path):
        fixed.append(str(nb_path.relative_to(notebooks_dir)))
    
    if fixed:
        print(f"Fixed {len(fixed)} notebooks:")
        for nb in fixed:
            print(f"  - {nb}")
    else:
        print("No changes needed")


if __name__ == '__main__':
    main()

