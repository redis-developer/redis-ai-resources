#!/usr/bin/env python3
"""
Execute only the failed notebooks.
"""

import subprocess
import sys
from pathlib import Path
import json
import tempfile
import shutil

def execute_notebook(notebook_path: Path) -> bool:
    """Execute a notebook and save it with outputs."""
    print(f"\n{'='*80}")
    print(f"Executing: {notebook_path.name}")
    print(f"{'='*80}")
    
    try:
        # Create a temporary copy
        temp_dir = Path(tempfile.mkdtemp())
        
        # Check if file is in jupytext percent format
        with open(notebook_path, 'r') as f:
            first_line = f.readline()
        
        is_jupytext = first_line.startswith('#%%')
        
        if is_jupytext:
            print("Converting jupytext format to .ipynb...")
            temp_ipynb = temp_dir / f"{notebook_path.stem}.ipynb"
            result = subprocess.run(
                ['jupytext', '--to', 'notebook', str(notebook_path), '-o', str(temp_ipynb)],
                capture_output=True,
                text=True,
                timeout=60
            )
            if result.returncode != 0:
                print(f"❌ Failed to convert: {result.stderr}")
                shutil.rmtree(temp_dir)
                return False
            temp_notebook = temp_ipynb
        else:
            # Already in .ipynb format
            temp_notebook = temp_dir / notebook_path.name
            shutil.copy(notebook_path, temp_notebook)
        
        # Execute the notebook
        print("Executing notebook...")
        result = subprocess.run(
            [
                'jupyter', 'nbconvert',
                '--to', 'notebook',
                '--execute',
                '--inplace',
                '--ExecutePreprocessor.timeout=600',
                '--ExecutePreprocessor.kernel_name=python3',
                str(temp_notebook)
            ],
            capture_output=True,
            text=True,
            timeout=700
        )
        
        if result.returncode != 0:
            print(f"❌ Execution failed:")
            print(result.stderr)
            shutil.rmtree(temp_dir)
            return False
        
        # Save the executed notebook
        if is_jupytext:
            # Save as .ipynb (executed version)
            output_ipynb = notebook_path.parent / f"{notebook_path.stem}_executed.ipynb"
            shutil.copy(temp_notebook, output_ipynb)
            print(f"✅ Saved executed notebook to: {output_ipynb.name}")
            
            # Also update the original jupytext file
            print("Converting back to jupytext format...")
            result = subprocess.run(
                ['jupytext', '--to', 'py:percent', str(temp_notebook), '-o', str(notebook_path)],
                capture_output=True,
                text=True,
                timeout=60
            )
            if result.returncode == 0:
                print(f"✅ Updated original jupytext file with outputs")
        else:
            # Replace original .ipynb with executed version
            shutil.copy(temp_notebook, notebook_path)
            print(f"✅ Saved executed notebook with outputs")
        
        # Cleanup
        shutil.rmtree(temp_dir)
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Main execution function."""
    
    # List of failed notebooks to execute
    notebooks = [
        "python-recipes/context-engineering/notebooks_v2/section-5-optimization-production/01_measuring_optimizing_performance.ipynb",
        "python-recipes/context-engineering/notebooks_v2/section-5-optimization-production/02_scaling_semantic_tool_selection.ipynb",
    ]
    
    workspace_root = Path(__file__).parent.parent.parent.parent
    
    print("=" * 80)
    print("EXECUTING FAILED NOTEBOOKS")
    print("=" * 80)
    print(f"Workspace root: {workspace_root}")
    
    # Load environment variables from parent .env file
    env_file = workspace_root / "python-recipes/context-engineering/.env"
    if env_file.exists():
        print(f"Loading environment from: {env_file}")
        from dotenv import load_dotenv
        load_dotenv(env_file)
        print("✅ Environment variables loaded")
    else:
        print(f"⚠️  No .env file found at {env_file}")
    
    print(f"Notebooks to execute: {len(notebooks)}")
    
    results = {}
    
    for notebook_rel_path in notebooks:
        notebook_path = workspace_root / notebook_rel_path
        
        if not notebook_path.exists():
            print(f"\n❌ Notebook not found: {notebook_path}")
            results[notebook_rel_path] = "NOT_FOUND"
            continue
        
        success = execute_notebook(notebook_path)
        results[notebook_rel_path] = "SUCCESS" if success else "FAILED"
    
    # Print summary
    print("\n" + "=" * 80)
    print("EXECUTION SUMMARY")
    print("=" * 80)
    for notebook_rel_path, status in results.items():
        notebook_name = Path(notebook_rel_path).name
        status_icon = "✅" if status == "SUCCESS" else "❌"
        print(f"{status_icon} {notebook_name}: {status}")
    
    # Exit with error if any failed
    if any(status == "FAILED" for status in results.values()):
        print("\n⚠️  Some notebooks failed to execute")
        sys.exit(1)
    else:
        print("\n✅ All notebooks executed successfully!")
        sys.exit(0)

if __name__ == "__main__":
    main()

