#!/usr/bin/env python3
"""
Fix specific errors in Section 5 notebooks.
"""

import json
from pathlib import Path

def fix_notebook_01(file_path: Path) -> bool:
    """Fix duplicate memory= parameter in notebook 01."""
    print(f"\nFixing: {file_path.name}")
    
    with open(file_path, 'r') as f:
        notebook = json.load(f)
    
    changes_made = False
    
    for cell in notebook.get('cells', []):
        if cell.get('cell_type') != 'code':
            continue
        
        source = cell.get('source', [])
        if not source:
            continue
        
        if isinstance(source, list):
            source_text = ''.join(source)
        else:
            source_text = source
        
        # Fix duplicate memory= parameter
        if 'memory=working_memory,\n            model_name="gpt-4o",\n            memory=working_memory' in source_text:
            print("  ✓ Fixing duplicate memory= parameter")
            source_text = source_text.replace(
                'memory=working_memory,\n            model_name="gpt-4o",\n            memory=working_memory',
                'memory=working_memory,\n            model_name="gpt-4o"'
            )
            cell['source'] = source_text.splitlines(keepends=True)
            changes_made = True
    
    if changes_made:
        with open(file_path, 'w') as f:
            json.dump(notebook, f, indent=1, ensure_ascii=False)
        print(f"  ✅ Fixed {file_path.name}")
        return True
    else:
        print(f"  ℹ️  No changes needed")
        return False

def fix_notebook_02(file_path: Path) -> bool:
    """Fix @tool decorator syntax in notebook 02."""
    print(f"\nFixing: {file_path.name}")
    
    with open(file_path, 'r') as f:
        notebook = json.load(f)
    
    changes_made = False
    
    for cell in notebook.get('cells', []):
        if cell.get('cell_type') != 'code':
            continue
        
        source = cell.get('source', [])
        if not source:
            continue
        
        if isinstance(source, list):
            source_text = ''.join(source)
        else:
            source_text = source
        
        # Fix @tool decorator - remove args_schema parameter
        if '@tool("check_prerequisites", args_schema=CheckPrerequisitesInput)' in source_text:
            print("  ✓ Fixing @tool decorator syntax")
            source_text = source_text.replace(
                '@tool("check_prerequisites", args_schema=CheckPrerequisitesInput)',
                '@tool'
            )
            cell['source'] = source_text.splitlines(keepends=True)
            changes_made = True
        
        if '@tool("get_course_schedule", args_schema=GetCourseScheduleInput)' in source_text:
            print("  ✓ Fixing @tool decorator syntax")
            source_text = source_text.replace(
                '@tool("get_course_schedule", args_schema=GetCourseScheduleInput)',
                '@tool'
            )
            cell['source'] = source_text.splitlines(keepends=True)
            changes_made = True
    
    if changes_made:
        with open(file_path, 'w') as f:
            json.dump(notebook, f, indent=1, ensure_ascii=False)
        print(f"  ✅ Fixed {file_path.name}")
        return True
    else:
        print(f"  ℹ️  No changes needed")
        return False

def main():
    """Main function."""
    print("=" * 80)
    print("FIXING SECTION 5 ERRORS")
    print("=" * 80)
    
    section5_dir = Path(__file__).parent / "section-5-optimization-production"
    
    # Fix notebook 01
    nb01 = section5_dir / "01_measuring_optimizing_performance.ipynb"
    if nb01.exists():
        fix_notebook_01(nb01)
    
    # Fix notebook 02
    nb02 = section5_dir / "02_scaling_semantic_tool_selection.ipynb"
    if nb02.exists():
        fix_notebook_02(nb02)
    
    print("\n" + "=" * 80)
    print("FIXES COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    main()

