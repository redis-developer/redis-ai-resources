#!/usr/bin/env python3
"""
Setup script for Agent Memory Server
This script ensures the Agent Memory Server is running with correct configuration
"""

import os
import subprocess
import sys
import time
from pathlib import Path

import requests
from dotenv import load_dotenv


def print_header(text):
    """Print a formatted header"""
    print(f"\n{text}")
    print("=" * len(text))


def print_status(emoji, message):
    """Print a status message"""
    print(f"{emoji} {message}")


def check_docker():
    """Check if Docker is running"""
    try:
        subprocess.run(
            ["docker", "info"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def check_container_running(container_name):
    """Check if a Docker container is running"""
    try:
        result = subprocess.run(
            [
                "docker",
                "ps",
                "--filter",
                f"name={container_name}",
                "--format",
                "{{.Names}}",
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        return container_name in result.stdout
    except subprocess.CalledProcessError:
        return False


def check_server_health(url, timeout=2):
    """Check if a server is responding"""
    try:
        response = requests.get(url, timeout=timeout)
        return response.status_code == 200
    except:
        return False


def check_redis_connection_errors(container_name):
    """Check Docker logs for Redis connection errors"""
    try:
        result = subprocess.run(
            ["docker", "logs", container_name, "--tail", "50"],
            capture_output=True,
            text=True,
            check=True,
        )
        return "ConnectionError" in result.stdout or "ConnectionError" in result.stderr
    except subprocess.CalledProcessError:
        return False


def stop_and_remove_container(container_name):
    """Stop and remove a Docker container"""
    try:
        subprocess.run(
            ["docker", "stop", container_name],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        subprocess.run(
            ["docker", "rm", container_name],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except:
        pass


def start_redis():
    """Start Redis container if not running"""
    if check_container_running("redis-stack-server"):
        print_status("✅", "Redis is running")
        return True

    print_status("⚠️ ", "Redis not running. Starting Redis...")
    try:
        subprocess.run(
            [
                "docker",
                "run",
                "-d",
                "--name",
                "redis-stack-server",
                "-p",
                "6379:6379",
                "redis/redis-stack-server:latest",
            ],
            check=True,
            stdout=subprocess.DEVNULL,
        )
        print_status("✅", "Redis started")
        return True
    except subprocess.CalledProcessError as e:
        print_status("❌", f"Failed to start Redis: {e}")
        return False


def start_agent_memory_server(openai_api_key):
    """Start Agent Memory Server with correct configuration"""
    print_status("🚀", "Starting Agent Memory Server...")

    try:
        subprocess.run(
            [
                "docker",
                "run",
                "-d",
                "--name",
                "agent-memory-server",
                "-p",
                "8088:8000",
                "-e",
                "REDIS_URL=redis://host.docker.internal:6379",
                "-e",
                f"OPENAI_API_KEY={openai_api_key}",
                "ghcr.io/redis/agent-memory-server:0.12.3",
            ],
            check=True,
            stdout=subprocess.DEVNULL,
        )

        # Wait for server to be ready
        print_status("⏳", "Waiting for server to be ready...")
        for i in range(30):
            if check_server_health("http://localhost:8088/v1/health"):
                print_status("✅", "Agent Memory Server is ready!")
                return True
            time.sleep(1)

        print_status("❌", "Timeout waiting for Agent Memory Server")
        print("   Check logs with: docker logs agent-memory-server")
        return False

    except subprocess.CalledProcessError as e:
        print_status("❌", f"Failed to start Agent Memory Server: {e}")
        return False


def verify_redis_connection():
    """Verify no Redis connection errors in logs"""
    print_status("🔍", "Verifying Redis connection...")
    time.sleep(2)

    if check_redis_connection_errors("agent-memory-server"):
        print_status("❌", "Redis connection error detected")
        print("   Check logs with: docker logs agent-memory-server")
        return False

    return True


def main():
    """Main setup function"""
    print_header("🔧 Agent Memory Server Setup")

    # Load environment variables
    env_file = Path(__file__).parent / ".env"
    if env_file.exists():
        load_dotenv(env_file)

    # Check OPENAI_API_KEY
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        print_status("❌", "Error: OPENAI_API_KEY not set")
        print("   Please set it in your .env file or environment")
        return False

    # Check Docker
    if not check_docker():
        print_status("❌", "Error: Docker is not running")
        print("   Please start Docker Desktop and try again")
        return False

    # Check Redis
    print_status("📊", "Checking Redis...")
    if not start_redis():
        return False

    # Check Agent Memory Server
    print_status("📊", "Checking Agent Memory Server...")
    if check_container_running("agent-memory-server"):
        print_status("🔍", "Agent Memory Server container exists. Checking health...")

        if check_server_health("http://localhost:8088/v1/health"):
            print_status("✅", "Agent Memory Server is running and healthy")

            # Check for Redis connection errors
            if check_redis_connection_errors("agent-memory-server"):
                print_status(
                    "⚠️ ",
                    "Detected Redis connection issues. Restarting with correct configuration...",
                )
                stop_and_remove_container("agent-memory-server")
            else:
                print_status("✅", "No Redis connection issues detected")
                print_header("✅ Setup Complete!")
                print("📊 Services Status:")
                print("   • Redis: Running on port 6379")
                print("   • Agent Memory Server: Running on port 8088")
                print("\n🎯 You can now run the notebooks!")
                return True
        else:
            print_status("⚠️ ", "Agent Memory Server not responding. Restarting...")
            stop_and_remove_container("agent-memory-server")

    # Start Agent Memory Server
    if not start_agent_memory_server(openai_api_key):
        return False

    # Verify Redis connection
    if not verify_redis_connection():
        return False

    # Success
    print_header("✅ Setup Complete!")
    print("📊 Services Status:")
    print("   • Redis: Running on port 6379")
    print("   • Agent Memory Server: Running on port 8088")
    print("\n🎯 You can now run the notebooks!")
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
