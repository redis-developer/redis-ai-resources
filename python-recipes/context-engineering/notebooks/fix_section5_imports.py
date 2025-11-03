#!/usr/bin/env python3
"""
Fix imports in Section 5 notebooks to use correct Agent Memory Client API.
"""

import json
from pathlib import Path

def fix_imports_in_notebook(file_path: Path) -> bool:
    """
    Fix imports in a Jupyter notebook JSON file.

    Args:
        file_path: Path to the notebook file

    Returns:
        True if changes were made, False otherwise
    """
    print(f"\nProcessing: {file_path.name}")

    # Load notebook JSON
    with open(file_path, 'r') as f:
        notebook = json.load(f)

    changes_made = False

    # Process each cell
    for cell in notebook.get('cells', []):
        if cell.get('cell_type') != 'code':
            continue

        source = cell.get('source', [])
        if not source:
            continue

        # Join source lines into a single string
        if isinstance(source, list):
            source_text = ''.join(source)
        else:
            source_text = source

        original_source = source_text

        # Fix 1: Replace AgentMemoryClient import
        if 'from agent_memory_client import AgentMemoryClient' in source_text:
            print(f"  ✓ Fixing AgentMemoryClient import in cell")
            source_text = source_text.replace(
                'from agent_memory_client import AgentMemoryClient\n',
                'from agent_memory_client import MemoryAPIClient, MemoryClientConfig\n'
            )
            source_text = source_text.replace(
                'from agent_memory_client import AgentMemoryClient',
                'from agent_memory_client import MemoryAPIClient, MemoryClientConfig'
            )
            changes_made = True

        # Fix 2: Replace AgentMemoryClient instantiation
        if 'memory_client = AgentMemoryClient(' in source_text:
            print(f"  ✓ Fixing AgentMemoryClient instantiation in cell")
            source_text = source_text.replace(
                'memory_client = AgentMemoryClient(base_url=AGENT_MEMORY_URL)',
                'memory_config = MemoryClientConfig(base_url=AGENT_MEMORY_URL)\nmemory_client = MemoryAPIClient(config=memory_config)'
            )
            changes_made = True

        # Fix 3: Replace get_working_memory calls (simple version)
        if 'await memory_client.get_working_memory(' in source_text:
            print(f"  ✓ Fixing get_working_memory call in cell")
            # This is a simplified fix - may need manual adjustment for complex cases
            source_text = source_text.replace(
                'working_memory = await memory_client.get_working_memory(',
                '_, working_memory = await memory_client.get_or_create_working_memory('
            )
            # Add model_name parameter if not present
            if 'model_name=' not in source_text and 'get_or_create_working_memory' in source_text:
                source_text = source_text.replace(
                    'session_id=SessionId(eq=state.session_id)\n        )',
                    'session_id=SessionId(eq=state.session_id),\n            model_name="gpt-4o"\n        )'
                )
            changes_made = True

        # Fix 4: Replace save_working_memory calls
        if 'await memory_client.save_working_memory(' in source_text:
            print(f"  ✓ Fixing save_working_memory call in cell")
            # This needs to be updated to use put_working_memory
            source_text = source_text.replace(
                'await memory_client.save_working_memory(',
                'await memory_client.put_working_memory('
            )
            # Update parameter names
            source_text = source_text.replace(
                'messages=state.messages',
                'memory=working_memory'
            )
            # Add model_name if not present
            if 'model_name=' not in source_text and 'put_working_memory' in source_text:
                source_text = source_text.replace(
                    'session_id=state.session_id,',
                    'session_id=state.session_id,\n            memory=working_memory,\n            model_name="gpt-4o",'
                )
            changes_made = True

        # Update cell source if changed
        if source_text != original_source:
            # Split back into lines for notebook format
            cell['source'] = source_text.splitlines(keepends=True)

    if changes_made:
        # Save updated notebook
        with open(file_path, 'w') as f:
            json.dump(notebook, f, indent=1, ensure_ascii=False)
        print(f"  ✅ Updated {file_path.name}")
        return True
    else:
        print(f"  ℹ️  No changes needed for {file_path.name}")
        return False

def main():
    """Main function."""
    print("=" * 80)
    print("FIXING SECTION 5 IMPORTS")
    print("=" * 80)

    # Find all notebooks in section 5
    section5_dir = Path(__file__).parent / "section-5-optimization-production"
    notebooks = list(section5_dir.glob("*.ipynb"))

    # Exclude checkpoint files
    notebooks = [nb for nb in notebooks if '.ipynb_checkpoints' not in str(nb)]

    print(f"\nFound {len(notebooks)} notebooks to process")

    fixed_count = 0
    for notebook in sorted(notebooks):
        if fix_imports_in_notebook(notebook):
            fixed_count += 1

    print("\n" + "=" * 80)
    print(f"SUMMARY: Fixed {fixed_count} out of {len(notebooks)} notebooks")
    print("=" * 80)

if __name__ == "__main__":
    main()

