#!/usr/bin/env python3
"""
Setup script for Progressive Context Engineering Notebooks

This script prepares your environment for the context engineering learning path.
Run this once before starting the notebooks.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


def print_header(title):
    """Print a formatted header."""
    print(f"\n{'='*60}")
    print(f"🚀 {title}")
    print(f"{'='*60}")


def print_step(step_num, description):
    """Print a formatted step."""
    print(f"\n📋 Step {step_num}: {description}")
    print("-" * 40)


def run_command(command, description, check=True):
    """Run a command and handle errors."""
    print(f"Running: {command}")
    try:
        result = subprocess.run(
            command, shell=True, check=check, capture_output=True, text=True
        )
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        if e.stderr:
            print(f"Error details: {e.stderr}")
        return False


def check_python_version():
    """Check if Python version is compatible."""
    print_step(1, "Checking Python Version")

    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python {version.major}.{version.minor} detected")
        print("   This project requires Python 3.8 or higher")
        print("   Please upgrade Python and try again")
        return False

    print(f"✅ Python {version.major}.{version.minor}.{version.micro} - Compatible")
    return True


def install_reference_agent():
    """Install the reference agent in editable mode."""
    print_step(2, "Installing Reference Agent")

    # Check if reference agent directory exists
    ref_agent_path = Path("../../reference-agent")
    if not ref_agent_path.exists():
        print(f"❌ Reference agent not found at {ref_agent_path.absolute()}")
        print(
            "   Please ensure you're running this from the enhanced-integration directory"
        )
        print("   and that the reference-agent directory exists")
        return False

    print(f"📁 Found reference agent at: {ref_agent_path.absolute()}")

    # Install in editable mode
    success = run_command(
        f"{sys.executable} -m pip install -e {ref_agent_path}",
        "Installing reference agent in editable mode",
    )

    if success:
        print("✅ Reference agent installed successfully")
        return True
    else:
        print("❌ Failed to install reference agent")
        return False


def install_dependencies():
    """Install required Python packages."""
    print_step(3, "Installing Required Dependencies")

    # Core dependencies for notebooks
    dependencies = [
        "python-dotenv",
        "jupyter",
        "nbformat",
        "redis",
        "openai",
        "langchain",
        "langchain-openai",
        "langchain-core",
        "scikit-learn",
        "numpy",
        "pandas",
    ]

    print("📦 Installing core dependencies...")
    for dep in dependencies:
        print(f"   Installing {dep}...")
        success = run_command(
            f"{sys.executable} -m pip install {dep}",
            f"Installing {dep}",
            check=False,  # Don't fail if one package fails
        )
        if success:
            print(f"   ✅ {dep} installed")
        else:
            print(f"   ⚠️  {dep} installation had issues (may already be installed)")

    print("✅ Dependencies installation complete")
    return True


def setup_environment_file():
    """Set up the .env file from template."""
    print_step(4, "Setting Up Environment File")

    env_example = Path(".env.example")
    env_file = Path(".env")

    if not env_example.exists():
        print("❌ .env.example file not found")
        return False

    if env_file.exists():
        print("⚠️  .env file already exists")
        response = input("   Do you want to overwrite it? (y/N): ").lower().strip()
        if response != "y":
            print("   Keeping existing .env file")
            return True

    # Copy template to .env
    shutil.copy(env_example, env_file)
    print("✅ Created .env file from template")

    print("\n📝 Next steps for .env configuration:")
    print("   1. Get your OpenAI API key: https://platform.openai.com/api-keys")
    print(
        "   2. Edit .env file and replace 'your_openai_api_key_here' with your actual key"
    )
    print("   3. Optional: Configure Redis URL if using remote Redis")

    return True


def check_optional_services():
    """Check status of optional services."""
    print_step(5, "Checking Optional Services")

    # Check Redis
    print("🔍 Checking Redis connection...")
    redis_available = run_command(
        f"{sys.executable} -c \"import redis; r=redis.Redis.from_url('redis://localhost:6379'); r.ping()\"",
        "Testing Redis connection",
        check=False,
    )

    if redis_available:
        print("✅ Redis is running and accessible")
    else:
        print("⚠️  Redis not available")
        print("   To start Redis with Docker:")
        print("   docker run -d -p 6379:6379 -p 8001:8001 redis/redis-stack")
        print("   (Redis is optional but recommended for full functionality)")

    return True


def verify_installation():
    """Verify the installation by importing key components."""
    print_step(6, "Verifying Installation")

    # Test imports
    test_imports = [
        ("redis_context_course.models", "Reference agent models"),
        ("redis_context_course.course_manager", "Course manager"),
        ("dotenv", "Python-dotenv"),
        ("openai", "OpenAI client"),
        ("langchain", "LangChain"),
    ]

    all_good = True
    for module, description in test_imports:
        try:
            __import__(module)
            print(f"✅ {description} - OK")
        except ImportError as e:
            print(f"❌ {description} - Failed: {e}")
            all_good = False

    if all_good:
        print("\n🎉 All components verified successfully!")
        return True
    else:
        print("\n❌ Some components failed verification")
        return False


def print_next_steps():
    """Print next steps for the user."""
    print_header("Setup Complete - Next Steps")

    print("🎯 Your environment is ready! Here's what to do next:")
    print()
    print("1. 📝 Configure your .env file:")
    print("   - Edit .env file in this directory")
    print("   - Add your OpenAI API key")
    print("   - Get key from: https://platform.openai.com/api-keys")
    print()
    print("2. 🚀 Start learning:")
    print("   - Run: jupyter notebook")
    print("   - Open: section-1-fundamentals/01_context_engineering_overview.ipynb")
    print("   - Follow the progressive learning path")
    print()
    print("3. 🔧 Optional enhancements:")
    print("   - Start Redis for full functionality:")
    print("     docker run -d -p 6379:6379 -p 8001:8001 redis/redis-stack")
    print("   - Access RedisInsight at: http://localhost:8001")
    print()
    print("📚 Learning Path:")
    print("   Section 1: Fundamentals → Section 2: RAG → Section 3: Memory")
    print("   → Section 4: Tool Selection → Section 5: Production Optimization")
    print()
    print("🎉 Happy learning! Build amazing context engineering systems!")


def main():
    """Main setup function."""
    print_header("Progressive Context Engineering Setup")
    print("This script will prepare your environment for the learning path.")
    print("Please ensure you're in the enhanced-integration directory.")

    # Confirm directory
    if not Path("../../notebooks_v2/section-1-fundamentals").exists():
        print(
            "\n❌ Error: Please run this script from the enhanced-integration directory"
        )
        print("   Expected to find: section-1-fundamentals/")
        sys.exit(1)

    # Run setup steps
    steps = [
        check_python_version,
        install_reference_agent,
        install_dependencies,
        setup_environment_file,
        check_optional_services,
        verify_installation,
    ]

    for step in steps:
        if not step():
            print(f"\n❌ Setup failed at: {step.__name__}")
            print("   Please resolve the issues above and try again")
            sys.exit(1)

    # Success!
    print_next_steps()


if __name__ == "__main__":
    main()
