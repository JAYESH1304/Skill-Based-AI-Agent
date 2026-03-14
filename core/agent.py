"""Main agent module with skill-based reasoning."""

from typing import List, Dict, Optional, Generator
import sys
from pathlib import Path
from core.azure_client import AzureOpenAIClient
from core.skill_loader import SkillLoader, Skill
from core.skill_matcher import SkillMatcher
from utils.logger import logger
from utils.helpers import count_tokens

class SkillBasedAgent:
    """Main agent that uses skills to complete tasks."""
    
    def __init__(self):
        """Initialize the skill-based agent."""
        logger.info("Initializing Skill-Based Agent...")
        
        # Initialize components
        self.azure_client = AzureOpenAIClient()
        self.skill_loader = SkillLoader()
        self.skill_matcher = SkillMatcher(self.skill_loader, self.azure_client)
        
        # Conversation state
        self.conversation_history: List[Dict[str, str]] = []
        self.current_skills: List[Skill] = []
        
        # Initialize script executor
        self._init_script_executor()
        
        logger.info("Agent initialized successfully")
    
    def _init_script_executor(self):
        """Initialize Python script executor."""
        try:
            # Add python-executor to path
            executor_path = Path("skills/python_executor")
            if executor_path.exists():
                sys.path.insert(0, str(executor_path))
                from skills.python_executor.tools import execute_python_script, format_execution_result, list_available_scripts
                self.execute_script = execute_python_script
                self.format_script_result = format_execution_result
                self.list_scripts = list_available_scripts
                self.script_executor_available = True
                logger.info("Python script executor initialized")
            else:
                self.script_executor_available = False
                logger.warning("Python script executor not available")
        except Exception as e:
            self.script_executor_available = False
            logger.warning(f"Could not initialize script executor: {e}")
    
    def _execute_python_script_tool(self, script_name: str, args: List[str] = None) -> str:
        """
        Execute a Python script and return formatted output.
        
        Args:
            script_name: Name of the script to execute
            args: Optional command-line arguments
            
        Returns:
            Formatted execution result
        """
        if not self.script_executor_available:
            return "Error: Script executor not available"
        
        try:
            # Ensure .py extension
            if not script_name.endswith('.py'):
                script_name += '.py'
            
            # Execute the script
            result = self.execute_script(script_name, args=args or [], timeout=30)
            
            # Format the result
            formatted = self.format_script_result(result)
            
            return formatted
            
        except FileNotFoundError:
            available = self.list_scripts()
            return f"Error: Script '{script_name}' not found.\nAvailable: {', '.join(available)}"
        except Exception as e:
            return f"Error executing script: {str(e)}"
    
    def _check_for_script_execution(self, user_query: str, matched_skills: List[Skill]) -> Optional[str]:
        """
        Check if the query requires script execution and execute if needed.
        
        Args:
            user_query: User's query
            matched_skills: List of matched skills
            
        Returns:
            Script execution result if executed, None otherwise
        """
        # Check if python-executor skill is matched
        has_executor_skill = any(skill.name == "python_executor" for skill in matched_skills)
        
        if not has_executor_skill:
            logger.debug("Python executor skill not matched")
            return None
            
        if not self.script_executor_available:
            logger.warning("Script executor not available")
            return None
        
        logger.info("Python executor skill matched, checking if script should run...")
        
        # Use LLM to determine if we should execute a script
        detection_prompt = f"""Based on this user query, determine if a Python script should be executed.

User Query: "{user_query}"

Available scripts:
{', '.join(self.list_scripts())}

If a script should be executed, respond with ONLY:
EXECUTE:<script_name>:<arg1>,<arg2>,...

If multiple args, separate with commas. If no args, just: EXECUTE:<script_name>:

If no script should be executed, respond with:
NO_EXECUTE

Examples:
- "run hello script" → EXECUTE:hello.py:
- "calculate 5 plus 3" → EXECUTE:calculator.py:add,5,3
- "what is 2+2" → NO_EXECUTE
- "fibonacci 20" → EXECUTE:fibonacci.py:20
- "multiply 15 by 7" → EXECUTE:calculator.py:multiply,15,7"""

        messages = [
            {"role": "system", "content": "You are a script execution detector. Respond only in the specified format."},
            {"role": "user", "content": detection_prompt}
        ]
        
        try:
            response = self.azure_client.chat_completion(messages, temperature=0, max_tokens=100)
            result = self.azure_client.get_response_text(response).strip()
            
            logger.info(f"Script detection result: {result}")
            
            if result.startswith("EXECUTE:"):
                parts = result.replace("EXECUTE:", "").split(":")
                script_name = parts[0].strip()
                args = [arg.strip() for arg in parts[1].split(",") if arg.strip()] if len(parts) > 1 and parts[1] else []
                
                logger.info(f"🚀 Executing script: {script_name} with args: {args}")
                output = self._execute_python_script_tool(script_name, args)
                logger.info(f"✅ Script execution completed, output length: {len(output)} chars")
                return output
            else:
                logger.info("No script execution needed")
            
        except Exception as e:
            logger.error(f"Error in script detection: {e}")
        
        return None
    
    def process_query(
        self,
        user_query: str,
        use_skills: bool = True,
        stream: bool = False
    ) -> str:
        """
        Process a user query with optional skill matching.
        
        Args:
            user_query: User's query or request
            use_skills: Whether to match and use skills
            stream: Whether to stream the response
            
        Returns:
            Agent's response or generator if streaming
        """
        logger.info(f"Processing query: {user_query[:100]}...")
        
        # Match skills if enabled
        matched_skills = []
        if use_skills:
            matched_skills = self.skill_matcher.match_skills(user_query)
            self.current_skills = matched_skills
        
        # Check if we should execute a script automatically BEFORE building messages
        script_output = None
        if use_skills and matched_skills:
            script_output = self._check_for_script_execution(user_query, matched_skills)
        
        # Build the actual user message to add to history
        if script_output:
            # Add script output to the user's query for context
            query_with_result = f"{user_query}\n\n[SCRIPT EXECUTION RESULT]\n{script_output}\n[END SCRIPT RESULT]"
        else:
            query_with_result = user_query
        
        # Add to history AFTER script execution
        self.conversation_history.append({
            "role": "user",
            "content": query_with_result
        })
        
        # Build messages for the LLM
        messages = self._build_messages(query_with_result, matched_skills, script_output)
        
        # Get response
        if stream:
            return self._stream_response(messages)
        else:
            return self._get_response(messages)
    
    def _build_messages(
        self,
        user_query: str,
        matched_skills: List[Skill],
        script_output: Optional[str] = None
    ) -> List[Dict[str, str]]:
        """
        Build message list for the LLM including skill instructions.
        
        Args:
            user_query: User's query
            matched_skills: List of matched skills
            script_output: Optional script execution output
            
        Returns:
            List of messages for the LLM
        """
        messages = []
        
        # System message with agent identity
        system_content = """You are a helpful AI assistant with access to specialized skills and Python script execution capabilities.

When skills are provided to you, follow their instructions carefully to complete the user's request.

IMPORTANT - Script Execution:
When you see [SCRIPT EXECUTION RESULT] in the user's message, it means a Python script has ALREADY been executed automatically. The output is provided for you to interpret and explain to the user.

- DO NOT say "I'll execute the script" or "Executing now..." - it's already done
- DO NOT provide terminal commands - execution happened automatically  
- DO read the script output carefully
- DO explain the results in a clear, natural way
- DO extract the key information from the output

Example:
User message: "Calculate 5 times 3

[SCRIPT EXECUTION RESULT]
═══════════════════
Executing: calculator.py
═══════════════════
📤 Output:
Result: 15.0
✅ Exit Code: 0
═══════════════════
[END SCRIPT RESULT]"

Your response: "5 × 3 = 15"

Always:
- Read and understand the skill instructions before responding
- Follow the skill's guidelines and recommendations
- Use script execution results when provided (marked with [SCRIPT EXECUTION RESULT])
- Provide clear, helpful, and accurate responses
- Ask for clarification if the request is ambiguous"""

        # Add skill instructions to system message
        if matched_skills:
            system_content += "\n\n## ACTIVE SKILLS\n\nYou have access to the following skills for this request:\n\n"
            
            for i, skill in enumerate(matched_skills, 1):
                system_content += f"### Skill {i}: {skill.name}\n\n"
                system_content += f"{skill.instructions}\n\n"
                system_content += "---\n\n"
            
            system_content += "\nPlease use the relevant skill instructions to help complete the user's request."
        
        # Add script execution information if available
        if script_output:
            system_content += "\n\n## SCRIPT EXECUTION\n\n"
            system_content += "A Python script was executed for this request. The output is included in the user's message.\n"
            system_content += "Use this output to provide a helpful response. Explain the results clearly to the user. Also ensure that you are not modifying this output. Give it as it is in your response. Also your output must match to the output of the executed script (for examples rows, columns) \n"
        
        messages.append({
            "role": "system",
            "content": system_content
        })
        
        # Add conversation history (last N messages to stay within context)
        max_history_messages = 10
        recent_history = self.conversation_history[-max_history_messages:] if len(self.conversation_history) > max_history_messages else self.conversation_history
        
        # Add history (excluding the current user message which is already in history)
        for msg in recent_history[:-1]:
            messages.append(msg)
        
        # Add current user message
        messages.append({
            "role": "user",
            "content": user_query
        })
        
        # Log token count
        total_tokens = sum(count_tokens(msg["content"]) for msg in messages)
        logger.debug(f"Total tokens in request: {total_tokens}")
        
        return messages
    
    def _get_response(self, messages: List[Dict[str, str]]) -> str:
        """
        Get a complete response from the LLM.
        
        Args:
            messages: List of messages
            
        Returns:
            Response text
        """
        try:
            response = self.azure_client.chat_completion(messages)
            response_text = self.azure_client.get_response_text(response)
            
            # Add assistant response to history
            self.conversation_history.append({
                "role": "assistant",
                "content": response_text
            })
            
            logger.info("Response generated successfully")
            return response_text
            
        except Exception as e:
            error_msg = f"Error generating response: {str(e)}"
            logger.error(error_msg)
            return f"I apologize, but I encountered an error: {str(e)}"
    
    def _stream_response(self, messages: List[Dict[str, str]]) -> Generator[str, None, None]:
        """
        Stream response from the LLM.
        
        Args:
            messages: List of messages
            
        Yields:
            Text chunks from the stream
        """
        try:
            stream = self.azure_client.chat_completion(messages, stream=True)
            
            full_response = ""
            for chunk in self.azure_client.stream_response(stream):
                full_response += chunk
                yield chunk
            
            # Add complete response to history
            self.conversation_history.append({
                "role": "assistant",
                "content": full_response
            })
            
            logger.info("Streaming response completed")
            
        except Exception as e:
            error_msg = f"\n\n[Error: {str(e)}]"
            logger.error(f"Error in streaming response: {str(e)}")
            
            # Still add error to history
            self.conversation_history.append({
                "role": "assistant",
                "content": error_msg
            })
            
            yield error_msg
    
    def get_available_skills(self) -> str:
        """
        Get a summary of available skills.
        
        Returns:
            Formatted string with skills information
        """
        return self.skill_loader.get_skills_summary()
    
    def use_specific_skill(self, skill_name: str, user_query: str) -> str:
        """
        Force use of a specific skill for a query.
        
        Args:
            skill_name: Name of the skill to use
            user_query: User's query
            
        Returns:
            Agent's response
        """
        skill = self.skill_matcher.force_match_skill(skill_name)
        
        if not skill:
            return f"Skill '{skill_name}' not found. Available skills:\n{self.get_available_skills()}"
        
        self.current_skills = [skill]
        
        # Build messages with the forced skill
        messages = self._build_messages(user_query, [skill])
        
        return self._get_response(messages)
    
    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history.clear()
        self.current_skills.clear()
        logger.info("Conversation history cleared")
    
    def reload_skills(self):
        """Reload all skills from disk."""
        self.skill_loader.reload_skills()
        logger.info("Skills reloaded")
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """
        Get the conversation history.
        
        Returns:
            List of conversation messages
        """
        return self.conversation_history.copy()