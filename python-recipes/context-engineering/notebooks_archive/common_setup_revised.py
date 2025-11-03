"""
Enhanced common setup code for Context Engineering notebooks.

This module provides a comprehensive setup function that:
1. Installs the redis_context_course package if needed
2. Loads environment variables from .env file with multiple fallback locations
3. Verifies required environment variables are set with interactive fallbacks
4. Checks service availability and configures appropriate learning modes
5. Provides helpful error messages and troubleshooting guidance
6. Supports offline/demo modes for environments without full service access

Usage in notebooks:
    import sys
    sys.path.insert(0, '..')
    from common_setup_revised import setup_notebook
    
    # Basic setup
    config = setup_notebook()
    
    # Setup with specific requirements
    config = setup_notebook(
        require_openai_key=True,
        require_memory_server=True,
        require_redis=True
    )
"""

import os
import sys
import subprocess
import getpass
import warnings
from pathlib import Path
from typing import Dict, Optional, Tuple, Any


class SetupConfig:
    """Configuration object returned by setup_notebook."""
    
    def __init__(self):
        self.learning_mode = "demo"
        self.services = {
            "redis": False,
            "memory_server": False,
            "openai": False,
            "package": False
        }
        self.environment = {}
        self.setup_successful = False
        self.warnings = []
        self.recommendations = []


def setup_notebook(
    require_openai_key: bool = False,
    require_memory_server: bool = False,
    require_redis: bool = False,
    interactive: bool = True,
    verbose: bool = True
) -> SetupConfig:
    """
    Set up the notebook environment with comprehensive configuration.
    
    Args:
        require_openai_key: If True, raises error if OPENAI_API_KEY is not available
        require_memory_server: If True, requires Agent Memory Server to be accessible
        require_redis: If True, requires Redis to be accessible
        interactive: If True, allows interactive prompts for missing configuration
        verbose: If True, prints detailed setup information
    
    Returns:
        SetupConfig object with setup results and configuration
    """
    config = SetupConfig()
    
    if verbose:
        print("🔧 Enhanced Context Engineering Environment Setup")
        print("=" * 60)
    
    # Step 1: Install package if needed
    config.services["package"] = _install_package_if_needed(verbose)
    
    # Step 2: Load environment variables
    config.environment = _load_environment_variables(verbose)
    
    # Step 3: Configure API keys
    _configure_api_keys(config, interactive, verbose)
    
    # Step 4: Check service availability
    _check_service_availability(config, verbose)
    
    # Step 5: Determine learning mode
    _determine_learning_mode(config, verbose)
    
    # Step 6: Validate requirements
    _validate_requirements(
        config, require_openai_key, require_memory_server, require_redis
    )
    
    # Step 7: Provide recommendations
    _generate_recommendations(config, verbose)
    
    if verbose:
        print("\n" + "=" * 60)
        if config.setup_successful:
            print("✅ Notebook setup complete!")
        else:
            print("⚠️  Setup completed with limitations")
        print("=" * 60)
    
    return config


def _install_package_if_needed(verbose: bool) -> bool:
    """Install the redis_context_course package if not already available."""
    try:
        import redis_context_course
        if verbose:
            print("✅ redis_context_course package already installed")
        return True
    except ImportError:
        if verbose:
            print("📦 Installing redis_context_course package...")
        
        # Find the reference-agent directory
        notebook_dir = Path.cwd()
        possible_paths = [
            notebook_dir / ".." / ".." / "reference-agent",
            notebook_dir / ".." / "reference-agent",
            notebook_dir / "reference-agent",
        ]
        
        reference_agent_path = None
        for path in possible_paths:
            if path.exists() and (path / "pyproject.toml").exists():
                reference_agent_path = path.resolve()
                break
        
        if not reference_agent_path:
            if verbose:
                print("❌ Could not find reference-agent directory")
                print("   Expected locations:")
                for path in possible_paths:
                    print(f"     {path}")
            return False
        
        # Install the package
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "-q", "-e", str(reference_agent_path)],
                capture_output=True,
                text=True,
                check=True
            )
            if verbose:
                print(f"✅ Package installed from {reference_agent_path}")
            return True
        except subprocess.CalledProcessError as e:
            if verbose:
                print(f"❌ Installation failed: {e.stderr}")
                print("   You may need to install manually:")
                print(f"   pip install -e {reference_agent_path}")
            return False


def _load_environment_variables(verbose: bool) -> Dict[str, str]:
    """Load environment variables from .env files with fallback locations."""
    env_config = {}
    
    # Try to install and import python-dotenv
    try:
        from dotenv import load_dotenv
    except ImportError:
        if verbose:
            print("📦 Installing python-dotenv...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "-q", "python-dotenv"], check=True)
            from dotenv import load_dotenv
            if verbose:
                print("✅ python-dotenv installed")
        except subprocess.CalledProcessError:
            if verbose:
                print("⚠️  Could not install python-dotenv")
            load_dotenv = None
    
    # Load from .env file if available
    if load_dotenv:
        notebook_dir = Path.cwd()
        env_paths = [
            notebook_dir / ".." / ".." / ".env",  # Course root
            notebook_dir / ".." / ".env",          # Notebooks root
            notebook_dir / ".env",                 # Current directory
        ]
        
        env_file_found = False
        for env_path in env_paths:
            if env_path.exists():
                load_dotenv(env_path)
                if verbose:
                    print(f"✅ Loaded environment from: {env_path}")
                env_file_found = True
                break
        
        if not env_file_found and verbose:
            print("⚠️  No .env file found - using system environment")
    
    # Set standardized defaults
    env_config = {
        "REDIS_URL": os.getenv("REDIS_URL", "redis://localhost:6379"),
        "AGENT_MEMORY_URL": os.getenv("AGENT_MEMORY_URL", "http://localhost:8088"),  # Standardized port
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY", "")
    }
    
    # Update environment
    for key, value in env_config.items():
        if value:
            os.environ[key] = value
    
    return env_config


def _configure_api_keys(config: SetupConfig, interactive: bool, verbose: bool) -> None:
    """Configure API keys with interactive fallback."""
    openai_key = config.environment.get("OPENAI_API_KEY", "")
    
    if openai_key and openai_key.startswith("sk-"):
        config.services["openai"] = True
        if verbose:
            print(f"✅ OpenAI API Key: {openai_key[:8]}...")
        return
    
    if verbose:
        print("🔑 OpenAI API Key not found in environment")
    
    if interactive:
        if verbose:
            print("\nTo get an OpenAI API key:")
            print("1. Visit https://platform.openai.com/api-keys")
            print("2. Sign in or create an account")
            print("3. Click 'Create new secret key'")
            print("4. Copy the key (starts with 'sk-')")
        
        try:
            user_key = getpass.getpass("\nEnter your OpenAI API key (or press Enter to continue in demo mode): ")
            if user_key.strip() and user_key.startswith("sk-"):
                os.environ["OPENAI_API_KEY"] = user_key.strip()
                config.environment["OPENAI_API_KEY"] = user_key.strip()
                config.services["openai"] = True
                if verbose:
                    print("✅ OpenAI API Key configured for this session")
            elif user_key.strip():
                if verbose:
                    print("⚠️  Invalid API key format (should start with 'sk-')")
                    print("   Continuing in demo mode...")
            else:
                if verbose:
                    print("⚠️  No API key provided - continuing in demo mode")
        except KeyboardInterrupt:
            if verbose:
                print("\n⚠️  Skipping API key configuration")
    else:
        if verbose:
            print("   Non-interactive mode - continuing without OpenAI API key")


def _check_service_availability(config: SetupConfig, verbose: bool) -> None:
    """Check which services are available."""
    if verbose:
        print("\n🔍 Checking Service Availability")
        print("-" * 40)
    
    # Check Redis
    try:
        import redis
        r = redis.from_url(config.environment["REDIS_URL"])
        r.ping()
        config.services["redis"] = True
        if verbose:
            print("✅ Redis: Available and responsive")
    except Exception as e:
        if verbose:
            print(f"❌ Redis: Not available ({type(e).__name__})")
    
    # Check Agent Memory Server
    try:
        import requests
        response = requests.get(f"{config.environment['AGENT_MEMORY_URL']}/v1/health", timeout=3)
        if response.status_code == 200:
            config.services["memory_server"] = True
            if verbose:
                print("✅ Agent Memory Server: Available and healthy")
        else:
            if verbose:
                print(f"❌ Agent Memory Server: Unhealthy (HTTP {response.status_code})")
    except Exception as e:
        if verbose:
            print(f"❌ Agent Memory Server: Not available ({type(e).__name__})")


def _determine_learning_mode(config: SetupConfig, verbose: bool) -> None:
    """Determine the appropriate learning mode based on available services."""
    services = config.services
    
    if all(services.values()):
        config.learning_mode = "full_interactive"
        description = "Full Interactive Mode - All features available"
    elif services["package"] and services["redis"] and services["openai"]:
        config.learning_mode = "redis_interactive"
        description = "Redis Interactive Mode - Course features available"
    elif services["package"] and services["redis"]:
        config.learning_mode = "redis_demo"
        description = "Redis Demo Mode - Course catalog available"
    elif services["package"]:
        config.learning_mode = "package_demo"
        description = "Package Demo Mode - Models and utilities available"
    else:
        config.learning_mode = "conceptual"
        description = "Conceptual Mode - Architecture and design patterns"
    
    os.environ["LEARNING_MODE"] = config.learning_mode
    
    if verbose:
        print(f"\n🎯 Learning Mode: {description}")


def _validate_requirements(
    config: SetupConfig,
    require_openai_key: bool,
    require_memory_server: bool,
    require_redis: bool
) -> None:
    """Validate that required services are available."""
    missing_requirements = []
    
    if require_openai_key and not config.services["openai"]:
        missing_requirements.append("OpenAI API key")
    
    if require_memory_server and not config.services["memory_server"]:
        missing_requirements.append("Agent Memory Server")
    
    if require_redis and not config.services["redis"]:
        missing_requirements.append("Redis")
    
    if missing_requirements:
        config.setup_successful = False
        config.warnings.append(f"Missing required services: {', '.join(missing_requirements)}")
        raise RuntimeError(
            f"Required services not available: {', '.join(missing_requirements)}\n"
            f"Please set up the missing services and try again."
        )
    else:
        config.setup_successful = True


def _generate_recommendations(config: SetupConfig, verbose: bool) -> None:
    """Generate setup recommendations based on current configuration."""
    if config.learning_mode == "full_interactive":
        if verbose:
            print("\n🎉 Perfect setup! All features are available.")
        return
    
    recommendations = []
    
    if not config.services["package"]:
        recommendations.append("📦 Install package: pip install -e ../../reference-agent")
    
    if not config.services["redis"]:
        recommendations.append("🔧 Start Redis: docker run -d -p 6379:6379 redis:8-alpine")
    
    if not config.services["memory_server"]:
        recommendations.append("🧠 Start Memory Server: docker-compose up -d (from course root)")
    
    if not config.services["openai"]:
        recommendations.append("🔑 Configure OpenAI API key in environment")
    
    config.recommendations = recommendations
    
    if verbose and recommendations:
        print("\n💡 To unlock more features:")
        for rec in recommendations:
            print(f"   {rec}")


# Convenience functions for common setups
def setup_basic() -> SetupConfig:
    """Basic setup without strict requirements."""
    return setup_notebook(
        require_openai_key=False,
        require_memory_server=False,
        require_redis=False
    )


def setup_with_redis() -> SetupConfig:
    """Setup requiring Redis for course search features."""
    return setup_notebook(
        require_openai_key=False,
        require_memory_server=False,
        require_redis=True
    )


def setup_full_interactive() -> SetupConfig:
    """Setup requiring all services for full interactive experience."""
    return setup_notebook(
        require_openai_key=True,
        require_memory_server=True,
        require_redis=True
    )


if __name__ == "__main__":
    # Test the setup
    print("Testing enhanced setup...")
    config = setup_notebook()
    print(f"\nSetup result: {config.learning_mode}")
    print(f"Services: {config.services}")
    if config.recommendations:
        print(f"Recommendations: {config.recommendations}")
