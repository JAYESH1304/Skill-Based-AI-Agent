"""
Example script demonstrating how to use the Skill-Based Agent programmatically.

This script shows various ways to interact with the agent without the Streamlit UI.
"""

from core.agent import SkillBasedAgent
from utils.logger import logger
import sys

def example_basic_usage():
    """Example 1: Basic agent usage with automatic skill matching."""
    print("\n" + "="*60)
    print("Example 1: Basic Usage with Automatic Skill Matching")
    print("="*60 + "\n")
    
    # Initialize the agent
    agent = SkillBasedAgent()
    
    # Ask a question - the agent will automatically match and use relevant skills
    query = "Write a short story about a robot learning to paint"
    print(f"Query: {query}\n")
    
    response = agent.process_query(query)
    print(f"Response:\n{response}\n")


def example_without_skills():
    """Example 2: Using the agent without skill matching."""
    print("\n" + "="*60)
    print("Example 2: Without Skills (Direct LLM Response)")
    print("="*60 + "\n")
    
    agent = SkillBasedAgent()
    
    # Simple factual question that doesn't need skills
    query = "What is the capital of France?"
    print(f"Query: {query}\n")
    
    response = agent.process_query(query, use_skills=False)
    print(f"Response:\n{response}\n")


def example_specific_skill():
    """Example 3: Force using a specific skill."""
    print("\n" + "="*60)
    print("Example 3: Using a Specific Skill")
    print("="*60 + "\n")
    
    agent = SkillBasedAgent()
    
    # Force use of code-assistant skill
    skill_name = "code-assistant"
    query = "Write a function to calculate the factorial of a number"
    
    print(f"Forcing skill: {skill_name}")
    print(f"Query: {query}\n")
    
    response = agent.use_specific_skill(skill_name, query)
    print(f"Response:\n{response}\n")


def example_streaming():
    """Example 4: Streaming responses."""
    print("\n" + "="*60)
    print("Example 4: Streaming Response")
    print("="*60 + "\n")
    
    agent = SkillBasedAgent()
    
    query = "Explain how neural networks work in simple terms"
    print(f"Query: {query}\n")
    print("Response (streaming):")
    
    # Stream the response
    for chunk in agent.process_query(query, stream=True):
        print(chunk, end="", flush=True)
    
    print("\n")


def example_conversation():
    """Example 5: Multi-turn conversation with context."""
    print("\n" + "="*60)
    print("Example 5: Multi-turn Conversation")
    print("="*60 + "\n")
    
    agent = SkillBasedAgent()
    
    # First message
    query1 = "Write a function to reverse a string in Python"
    print(f"User: {query1}")
    response1 = agent.process_query(query1)
    print(f"Agent: {response1[:200]}...\n")
    
    # Follow-up message (agent maintains context)
    query2 = "Now optimize it for very long strings"
    print(f"User: {query2}")
    response2 = agent.process_query(query2)
    print(f"Agent: {response2[:200]}...\n")
    
    # View conversation history
    print("Conversation History:")
    history = agent.get_conversation_history()
    print(f"Total messages: {len(history)}")


def example_list_skills():
    """Example 6: List all available skills."""
    print("\n" + "="*60)
    print("Example 6: List Available Skills")
    print("="*60 + "\n")
    
    agent = SkillBasedAgent()
    
    # Get skills summary
    skills_summary = agent.get_available_skills()
    print(skills_summary)


def example_error_handling():
    """Example 7: Error handling and edge cases."""
    print("\n" + "="*60)
    print("Example 7: Error Handling")
    print("="*60 + "\n")
    
    agent = SkillBasedAgent()
    
    # Try to use a non-existent skill
    print("Attempting to use non-existent skill...")
    response = agent.use_specific_skill("non-existent-skill", "Test query")
    print(f"Response: {response}\n")
    
    # Clear conversation history
    print("Clearing conversation history...")
    agent.clear_history()
    print("History cleared!\n")
    
    # Reload skills
    print("Reloading skills...")
    agent.reload_skills()
    print("Skills reloaded!\n")


def interactive_mode():
    """Interactive mode: Chat with the agent."""
    print("\n" + "="*60)
    print("Interactive Mode - Chat with the Agent")
    print("="*60)
    print("\nType 'quit' to exit, 'clear' to clear history, 'skills' to list skills\n")
    
    agent = SkillBasedAgent()
    
    while True:
        try:
            user_input = input("\nYou: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() == 'quit':
                print("Goodbye!")
                break
            
            if user_input.lower() == 'clear':
                agent.clear_history()
                print("History cleared!")
                continue
            
            if user_input.lower() == 'skills':
                print(agent.get_available_skills())
                continue
            
            print("\nAgent: ", end="", flush=True)
            
            # Stream the response
            for chunk in agent.process_query(user_input, stream=True):
                print(chunk, end="", flush=True)
            
            print()  # New line after response
            
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"\nError: {str(e)}")


def main():
    """Main function to run examples."""
    print("\n" + "="*60)
    print("Skill-Based Agent - Example Usage")
    print("="*60)
    
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
        
        if mode == "interactive" or mode == "chat":
            interactive_mode()
            return
    
    # Run all examples
    examples = [
        example_basic_usage,
        example_without_skills,
        example_specific_skill,
        example_streaming,
        example_conversation,
        example_list_skills,
        example_error_handling,
    ]
    
    print("\nRunning examples...")
    print("Press Enter to continue between examples, or Ctrl+C to stop.\n")
    
    try:
        for i, example_func in enumerate(examples, 1):
            example_func()
            if i < len(examples):
                input("\nPress Enter to continue to next example...")
    except KeyboardInterrupt:
        print("\n\nExamples stopped.")
    
    print("\n" + "="*60)
    print("Examples completed!")
    print("="*60)
    print("\nTo run interactive mode: python example_usage.py interactive")
    print("To run Streamlit UI: streamlit run ui/streamlit_app.py\n")


if __name__ == "__main__":
    main()