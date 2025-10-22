"""
Common setup code for Context Engineering notebooks.

This module provides a standard setup function that:
1. Installs the redis_context_course package if needed
2. Loads environment variables from .env file
3. Verifies required environment variables are set
4. Provides helpful error messages if setup is incomplete

Usage in notebooks:
    #%%
    # Run common setup
    import sys
    sys.path.insert(0, '..')
    from common_setup import setup_notebook
    
    setup_notebook()
"""

import os
import sys
import subprocess
from pathlib import Path


def setup_notebook(require_openai_key=True, require_memory_server=False):
    """
    Set up the notebook environment.
    
    Args:
        require_openai_key: If True, raises error if OPENAI_API_KEY is not set
        require_memory_server: If True, checks that Agent Memory Server is accessible
    """
    print("🔧 Setting up notebook environment...")
    print("=" * 60)
    
    # Step 1: Install the redis_context_course package if needed
    try:
        import redis_context_course
        print("✅ redis_context_course package already installed")
    except ImportError:
        print("📦 Installing redis_context_course package...")
        
        # Find the reference-agent directory
        notebook_dir = Path.cwd()
        reference_agent_path = None
        
        # Try common locations
        possible_paths = [
            notebook_dir / ".." / ".." / "reference-agent",  # From section notebooks
            notebook_dir / ".." / "reference-agent",          # From notebooks root
            notebook_dir / "reference-agent",                 # From context-engineering root
        ]
        
        for path in possible_paths:
            if path.exists() and (path / "setup.py").exists():
                reference_agent_path = path.resolve()
                break
        
        if not reference_agent_path:
            print("❌ Could not find reference-agent directory")
            print("   Please run from the notebooks directory or ensure reference-agent exists")
            raise RuntimeError("reference-agent directory not found")
        
        # Install the package
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "-q", "-e", str(reference_agent_path)],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print(f"✅ Installed redis_context_course from {reference_agent_path}")
        else:
            print(f"❌ Failed to install package: {result.stderr}")
            raise RuntimeError(f"Package installation failed: {result.stderr}")
    
    # Step 2: Load environment variables from .env file
    try:
        from dotenv import load_dotenv
        
        # Find the .env file (should be in context-engineering root)
        notebook_dir = Path.cwd()
        env_file = None
        
        # Try common locations
        possible_env_paths = [
            notebook_dir / ".." / ".." / ".env",  # From section notebooks
            notebook_dir / ".." / ".env",          # From notebooks root
            notebook_dir / ".env",                 # From context-engineering root
        ]
        
        for path in possible_env_paths:
            if path.exists():
                env_file = path.resolve()
                break
        
        if env_file:
            load_dotenv(env_file)
            print(f"✅ Loaded environment variables from {env_file}")
        else:
            print("⚠️  No .env file found - will use system environment variables")
            print("   To create one, see SETUP.md")
    
    except ImportError:
        print("⚠️  python-dotenv not installed - skipping .env file loading")
        print("   Install with: pip install python-dotenv")
    
    # Step 3: Verify required environment variables
    print("\n📋 Environment Variables:")
    print("-" * 60)
    
    # Check OPENAI_API_KEY
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        print(f"✅ OPENAI_API_KEY: Set ({openai_key[:8]}...)")
    else:
        print("❌ OPENAI_API_KEY: Not set")
        if require_openai_key:
            raise ValueError(
                "OPENAI_API_KEY not found. Please:\n"
                "1. Create a .env file in python-recipes/context-engineering/\n"
                "2. Add: OPENAI_API_KEY=your-key-here\n"
                "3. See SETUP.md for detailed instructions"
            )
    
    # Check REDIS_URL
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
    print(f"✅ REDIS_URL: {redis_url}")
    
    # Check AGENT_MEMORY_URL
    memory_url = os.getenv("AGENT_MEMORY_URL", "http://localhost:8088")
    print(f"✅ AGENT_MEMORY_URL: {memory_url}")
    
    # Step 4: Check Agent Memory Server if required
    if require_memory_server:
        print("\n🔍 Checking Agent Memory Server...")
        print("-" * 60)
        try:
            import requests
            response = requests.get(f"{memory_url}/health", timeout=2)
            if response.status_code == 200:
                print(f"✅ Agent Memory Server is running at {memory_url}")
            else:
                print(f"⚠️  Agent Memory Server returned status {response.status_code}")
                raise RuntimeError(
                    f"Agent Memory Server is not healthy. Please run:\n"
                    f"  cd python-recipes/context-engineering\n"
                    f"  docker-compose up -d"
                )
        except ImportError:
            print("⚠️  requests library not installed - skipping health check")
            print("   Install with: pip install requests")
        except Exception as e:
            print(f"❌ Could not connect to Agent Memory Server: {e}")
            raise RuntimeError(
                f"Agent Memory Server is not accessible at {memory_url}\n"
                f"Please run:\n"
                f"  cd python-recipes/context-engineering\n"
                f"  docker-compose up -d\n"
                f"Then verify with: curl {memory_url}/health"
            )
    
    print("\n" + "=" * 60)
    print("✅ Notebook setup complete!")
    print("=" * 60)


if __name__ == "__main__":
    # Test the setup
    setup_notebook(require_openai_key=True, require_memory_server=False)

