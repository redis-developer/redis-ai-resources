#!/usr/bin/env python3
"""
Demo script for Oregon Trail Agent

This script demonstrates the Oregon Trail Agent with a single test scenario.
Requires OpenAI API key to be set.
"""

import os
import sys

def check_api_key():
    """Check if OpenAI API key is set"""
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ OpenAI API key not set!")
        print("Please set your API key:")
        print("export OPENAI_API_KEY='your-key-here'")
        return False
    return True

def run_demo():
    """Run a simple demo of the Oregon Trail Agent"""
    print("🎮 Oregon Trail Agent Demo")
    print("="*50)
    
    if not check_api_key():
        return False
    
    try:
        # Import the agent (this will now work since API key is set)
        sys.path.append('nk_scripts')
        from full_featured_agent import OregonTrailAgent, run_scenario
        
        print("✅ Agent imported successfully!")
        print("🚀 Creating Oregon Trail Agent...")
        
        # Create the agent
        agent = OregonTrailAgent()
        print("✅ Agent created successfully!")
        
        # Run a simple test scenario
        print("\n🎯 Running demo scenario...")
        test_scenario = {
            "name": "Demo: Wagon Leader Name",
            "question": "What is the first name of the wagon leader?",
            "answer": "Art",
            "type": "free-form"
        }
        
        success = run_scenario(agent, test_scenario)
        
        if success:
            print("\n🎉 Demo completed successfully!")
            print("\nThe agent is working correctly. You can now:")
            print("1. Run the full test suite: python nk_scripts/full_featured_agent.py")
            print("2. Explore the code in nk_scripts/full_featured_agent.py")
            print("3. Try the Context Course Agent next")
            return True
        else:
            print("\n❌ Demo failed. Check the output above for details.")
            return False
            
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        print("\nTroubleshooting tips:")
        print("1. Make sure Redis is running: docker run -d --name redis -p 6379:6379 redis:8-alpine")
        print("2. Check your OpenAI API key is valid")
        print("3. Ensure you're in the virtual environment: source python-recipes/context-engineering/venv/bin/activate")
        return False

if __name__ == "__main__":
    success = run_demo()
    if not success:
        sys.exit(1)
