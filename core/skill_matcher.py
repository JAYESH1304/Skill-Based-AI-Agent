"""Skill matcher module for matching queries to relevant skills."""

from typing import List, Tuple, Optional
from core.skill_loader import Skill, SkillLoader
from core.azure_client import AzureOpenAIClient
from utils.logger import logger

class SkillMatcher:
    """Matches user queries to relevant skills using LLM."""
    
    def __init__(self, skill_loader: SkillLoader, azure_client: AzureOpenAIClient):
        """
        Initialize the skill matcher.
        
        Args:
            skill_loader: SkillLoader instance
            azure_client: AzureOpenAIClient instance
        """
        self.skill_loader = skill_loader
        self.azure_client = azure_client
    
    def match_skills(self, user_query: str, top_k: int = 3) -> List[Skill]:
        """
        Match user query to relevant skills.
        
        Args:
            user_query: User's query or request
            top_k: Maximum number of skills to return
            
        Returns:
            List of relevant skills
        """
        all_skills = self.skill_loader.get_all_skills()
        
        if not all_skills:
            logger.warning("No skills available for matching")
            return []
        
        if len(all_skills) == 1:
            logger.info(f"Only one skill available, returning: {all_skills[0].name}")
            return all_skills
        
        # Use LLM to match skills
        matched_skills = self._llm_match(user_query, all_skills, top_k)
        
        logger.info(f"Matched {len(matched_skills)} skills for query: {user_query[:50]}...")
        for skill in matched_skills:
            logger.debug(f"  - {skill.name}")
        
        return matched_skills
    
    def _llm_match(self, user_query: str, skills: List[Skill], top_k: int) -> List[Skill]:
        """
        Use LLM to match skills to the query.
        
        Args:
            user_query: User's query
            skills: List of available skills
            top_k: Maximum number of skills to return
            
        Returns:
            List of matched skills
        """
        # Create skill descriptions for the prompt
        skill_list = []
        for i, skill in enumerate(skills):
            skill_list.append(f"{i+1}. **{skill.name}**: {skill.description}")
        
        skills_text = "\n".join(skill_list)
        
        # Create matching prompt
        system_prompt = """You are a skill matching assistant. Your job is to analyze a user's query and determine which skills are most relevant to help answer or complete their request.

You will be given:
1. A user query
2. A list of available skills with descriptions

Your task:
- Analyze the user's query carefully
- Identify which skills would be most helpful
- Return ONLY the skill numbers (e.g., "1, 3" or "2") as a comma-separated list
- If no skills are relevant, return "none"
- Return at most the top 3 most relevant skills

Be selective - only choose skills that are clearly relevant to the query."""

        user_prompt = f"""User Query: "{user_query}"

Available Skills:
{skills_text}

Which skill numbers are most relevant? Return only numbers separated by commas (e.g., "1, 3" or "2"), or "none" if no skills match."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        try:
            response = self.azure_client.chat_completion(messages, temperature=0.3, max_tokens=50)
            result = self.azure_client.get_response_text(response).strip().lower()
            
            logger.debug(f"LLM matching result: {result}")
            
            # Parse the response
            if result == "none" or not result:
                return []
            
            # Extract skill numbers
            matched_skills = []
            try:
                # Parse comma-separated numbers
                skill_numbers = [int(n.strip()) for n in result.split(',') if n.strip().isdigit()]
                
                for num in skill_numbers[:top_k]:
                    if 1 <= num <= len(skills):
                        matched_skills.append(skills[num - 1])
                
            except ValueError as e:
                logger.error(f"Error parsing skill numbers: {e}")
                # Fallback: return first skill if available
                if skills:
                    matched_skills = [skills[0]]
            
            return matched_skills
            
        except Exception as e:
            logger.error(f"Error in LLM matching: {str(e)}")
            # Fallback: return first skill
            return [skills[0]] if skills else []
    
    def force_match_skill(self, skill_name: str) -> Optional[Skill]:
        """
        Force match a specific skill by name.
        
        Args:
            skill_name: Name of the skill to match
            
        Returns:
            Skill object or None if not found
        """
        skill = self.skill_loader.get_skill(skill_name)
        if skill:
            logger.info(f"Force matched skill: {skill_name}")
        else:
            logger.warning(f"Skill not found: {skill_name}")
        return skill