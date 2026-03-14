"""
Test script for automatic script execution.

Run this to verify the agent can automatically execute scripts.
"""

import sys
from pathlib import Path

# Add project to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.agent import SkillBasedAgent

def test_automatic_execution():
    """Test automatic script execution."""
    print("="*60)
    print("Testing Automatic Script Execution")
    print("="*60)
    print()
    
    # Initialize agent
    print("Initializing agent...")
    agent = SkillBasedAgent()
    print("✓ Agent initialized")
    print()
    
    # Test queries
    test_queries = [
        "Run the calculator.py script to calculate 11 multiplied by 7",
        "Run the abc.py script and give me the output",
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{'='*60}")
        print(f"Test {i}: {query}")
        print("="*60)
        
        try:
            response = agent.process_query(query, use_skills=True, stream=False)
            print(f"\n📤 Agent Response:")
            print(response)
            print()
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
        
        print("-"*60)
    
    print("\n" + "="*60)
    print("Testing Complete!")
    print("="*60)

if __name__ == "__main__":
    test_automatic_execution()