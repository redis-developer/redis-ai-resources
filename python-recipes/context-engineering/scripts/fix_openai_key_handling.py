#!/usr/bin/env python3
"""
Fix OpenAI API key handling in notebooks to use real keys when available.

This script updates notebooks to not set dummy keys in CI environments,
allowing them to use the real OPENAI_API_KEY from the environment.
"""

import json
import sys
from pathlib import Path


def fix_notebook(notebook_path: Path) -> bool:
    """Fix OpenAI key handling in a single notebook."""
    print(f"Processing: {notebook_path}")
    
    with open(notebook_path, 'r') as f:
        nb = json.load(f)
    
    modified = False
    
    for cell in nb['cells']:
        if cell['cell_type'] == 'code':
            # Check if this cell has the _set_env function
            source_text = ''.join(cell['source'])
            if '_set_env' in source_text and 'sk-dummy-key-for-testing-purposes-only' in source_text:
                # Replace the dummy key logic
                new_source = []
                for line in cell['source']:
                    if 'sk-dummy-key-for-testing-purposes-only' in line:
                        # Skip setting a dummy key - just pass
                        new_source.append('            pass  # Let it fail if key is actually needed\n')
                        modified = True
                    elif '# Non-interactive environment (like CI) - use a dummy key' in line:
                        new_source.append('            # Non-interactive environment (like CI)\n')
                        modified = True
                    elif 'Non-interactive environment detected. Using dummy' in line:
                        new_source.append('            print(f"⚠️  {key} not found in environment. Some features may not work.")\n')
                        modified = True
                    else:
                        new_source.append(line)
                
                if modified:
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
            if fix_notebook(notebook_path):
                total_updated += 1
    
    print(f"\n✅ Updated {total_updated} notebooks")
    return 0


if __name__ == '__main__':
    sys.exit(main())

