#!/usr/bin/env python3
"""
Centralized setup check for Context Engineering notebooks.

This module provides reusable functions for verifying that all required services
(Redis, Agent Memory Server) are running before executing notebook code.

Usage in notebooks:
    from setup_check import run_setup_check
    run_setup_check()
"""

import subprocess
import sys
from pathlib import Path


def run_setup_check(verbose: bool = True) -> bool:
    """
    Run the automated setup check to ensure Redis and Agent Memory Server are running.
    
    This function:
    1. Locates the setup_agent_memory_server.py script
    2. Executes it to verify/start required services
    3. Displays the output to the user
    4. Returns success/failure status
    
    Args:
        verbose: If True, print detailed output. If False, only print summary.
    
    Returns:
        bool: True if all services are ready, False otherwise
    """
    # Path to setup script (relative to this file)
    setup_script = Path(__file__).parent.parent / "reference-agent" / "setup_agent_memory_server.py"
    
    if not setup_script.exists():
        print("⚠️  Setup script not found at:", setup_script)
        print("   Please ensure the reference-agent directory exists.")
        print("   Expected location: ../reference-agent/setup_agent_memory_server.py")
        return False
    
    if verbose:
        print("=" * 80)
        print("🔧 AUTOMATED SETUP CHECK")
        print("=" * 80)
        print("\nRunning setup script to verify services...\n")
    
    try:
        # Run the setup script
        result = subprocess.run(
            [sys.executable, str(setup_script)],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        # Display output
        if verbose:
            print(result.stdout)
            if result.stderr:
                print("Errors/Warnings:")
                print(result.stderr)
        
        # Check result
        if result.returncode == 0:
            if verbose:
                print("\n" + "=" * 80)
                print("✅ ALL SERVICES ARE READY!")
                print("=" * 80)
            else:
                print("✅ Setup check passed - all services ready")
            return True
        else:
            print("\n" + "=" * 80)
            print("⚠️  SETUP CHECK FAILED")
            print("=" * 80)
            print("\nSome services may not be running properly.")
            print("Please review the output above and ensure:")
            print("  1. Docker Desktop is running")
            print("  2. Redis is accessible on port 6379")
            print("  3. Agent Memory Server is accessible on port 8088")
            print("\nFor manual setup, see: SETUP_GUIDE.md")
            return False
            
    except subprocess.TimeoutExpired:
        print("⚠️  Setup check timed out after 30 seconds")
        print("   Services may be starting. Please wait and try again.")
        return False
    except Exception as e:
        print(f"❌ Error running setup check: {e}")
        return False


def check_services_quick() -> dict:
    """
    Quick check of service availability without running full setup.
    
    Returns:
        dict: Status of each service (redis, memory_server, env_vars)
    """
    import os
    import redis
    import requests
    from dotenv import load_dotenv
    
    # Load environment variables
    env_path = Path(__file__).parent.parent / "reference-agent" / ".env"
    load_dotenv(dotenv_path=env_path)
    
    status = {
        "redis": False,
        "memory_server": False,
        "env_vars": False
    }
    
    # Check environment variables
    if os.getenv("OPENAI_API_KEY"):
        status["env_vars"] = True
    
    # Check Redis
    try:
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        r = redis.from_url(redis_url)
        r.ping()
        status["redis"] = True
    except:
        pass
    
    # Check Memory Server
    try:
        memory_url = os.getenv("AGENT_MEMORY_URL", "http://localhost:8088")
        response = requests.get(f"{memory_url}/health", timeout=2)
        if response.status_code == 200:
            status["memory_server"] = True
    except:
        pass
    
    return status


def print_service_status(status: dict = None):
    """
    Print a formatted summary of service status.
    
    Args:
        status: Optional status dict from check_services_quick().
                If None, will run the check.
    """
    if status is None:
        status = check_services_quick()
    
    print("\n" + "=" * 80)
    print("📊 SERVICE STATUS")
    print("=" * 80)
    print(f"\n{'✅' if status['env_vars'] else '❌'} Environment Variables (OPENAI_API_KEY)")
    print(f"{'✅' if status['redis'] else '❌'} Redis (port 6379)")
    print(f"{'✅' if status['memory_server'] else '❌'} Agent Memory Server (port 8088)")
    
    all_ready = all(status.values())
    print("\n" + "=" * 80)
    if all_ready:
        print("✅ All services are ready!")
    else:
        print("⚠️  Some services are not ready. Run setup_check.run_setup_check()")
    print("=" * 80 + "\n")
    
    return all_ready


if __name__ == "__main__":
    """Allow running this module directly for testing."""
    success = run_setup_check(verbose=True)
    sys.exit(0 if success else 1)

