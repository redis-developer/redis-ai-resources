#!/usr/bin/env python3
"""
Fix save_working_memory calls in notebooks to use put_working_memory.
"""

import json
import sys
from pathlib import Path


def fix_save_working_memory_call(cell_source):
    """
    Replace save_working_memory calls with put_working_memory.
    
    Converts:
        await memory_client.save_working_memory(
            session_id=session_id,
            messages=messages
        )
    
    To:
        from agent_memory_client import WorkingMemory, MemoryMessage
        
        memory_messages = [MemoryMessage(**msg) for msg in messages]
        working_memory = WorkingMemory(
            session_id=session_id,
            user_id=user_id,
            messages=memory_messages,
            memories=[],
            data={}
        )
        
        await memory_client.put_working_memory(
            session_id=session_id,
            memory=working_memory,
            user_id=user_id,
            model_name="gpt-4o"
        )
    """
    source_text = ''.join(cell_source)
    
    # Skip if this is just documentation
    if 'save_working_memory()' in source_text and ('print(' in source_text or 'MemoryClient provides' in source_text):
        # Just update the documentation text
        new_source = []
        for line in cell_source:
            line = line.replace('save_working_memory()', 'put_working_memory()')
            line = line.replace('get_working_memory()', 'get_or_create_working_memory()')
            new_source.append(line)
        return new_source
    
    # Check if this cell has an actual save_working_memory call
    if 'await memory_client.save_working_memory(' not in source_text:
        return cell_source
    
    new_source = []
    in_save_call = False
    save_indent = ''
    session_id_var = 'session_id'
    messages_var = 'messages'
    user_id_var = 'user_id'
    
    # First pass: find the variables used
    for line in cell_source:
        if 'await memory_client.save_working_memory(' in line:
            save_indent = line[:len(line) - len(line.lstrip())]
            in_save_call = True
        elif in_save_call:
            if 'session_id=' in line:
                session_id_var = line.split('session_id=')[1].split(',')[0].split(')')[0].strip()
            elif 'messages=' in line:
                messages_var = line.split('messages=')[1].split(',')[0].split(')')[0].strip()
            if ')' in line:
                in_save_call = False
    
    # Check if user_id is defined in the cell
    if 'user_id' not in source_text:
        # Try to find student_id or demo_student
        if 'student_id' in source_text:
            user_id_var = 'student_id'
        elif 'demo_student' in source_text:
            user_id_var = '"demo_student_working_memory"'
        else:
            user_id_var = '"demo_user"'
    
    # Second pass: replace the call
    in_save_call = False
    skip_lines = 0
    
    for i, line in enumerate(cell_source):
        if skip_lines > 0:
            skip_lines -= 1
            continue
            
        if 'await memory_client.save_working_memory(' in line:
            # Add imports if not already present
            if 'from agent_memory_client import WorkingMemory' not in source_text:
                new_source.append(f'{save_indent}from agent_memory_client import WorkingMemory, MemoryMessage\n')
                new_source.append(f'{save_indent}\n')
            
            # Add conversion code
            new_source.append(f'{save_indent}# Convert messages to MemoryMessage format\n')
            new_source.append(f'{save_indent}memory_messages = [MemoryMessage(**msg) for msg in {messages_var}]\n')
            new_source.append(f'{save_indent}\n')
            new_source.append(f'{save_indent}# Create WorkingMemory object\n')
            new_source.append(f'{save_indent}working_memory = WorkingMemory(\n')
            new_source.append(f'{save_indent}    session_id={session_id_var},\n')
            new_source.append(f'{save_indent}    user_id={user_id_var},\n')
            new_source.append(f'{save_indent}    messages=memory_messages,\n')
            new_source.append(f'{save_indent}    memories=[],\n')
            new_source.append(f'{save_indent}    data={{}}\n')
            new_source.append(f'{save_indent})\n')
            new_source.append(f'{save_indent}\n')
            new_source.append(f'{save_indent}await memory_client.put_working_memory(\n')
            new_source.append(f'{save_indent}    session_id={session_id_var},\n')
            new_source.append(f'{save_indent}    memory=working_memory,\n')
            new_source.append(f'{save_indent}    user_id={user_id_var},\n')
            new_source.append(f'{save_indent}    model_name="gpt-4o"\n')
            new_source.append(f'{save_indent})\n')
            
            # Skip the rest of the save_working_memory call
            in_save_call = True
        elif in_save_call:
            if ')' in line:
                in_save_call = False
            # Skip this line (part of old call)
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
            cell['source'] = fix_save_working_memory_call(cell['source'])
            
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
    
    # Find all notebooks with save_working_memory
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

