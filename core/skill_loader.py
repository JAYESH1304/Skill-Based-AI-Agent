"""Skill loader module for discovering and loading skills."""

import os
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass
from config import Config
from utils.logger import logger

@dataclass
class Skill:
    """Represents a skill with its metadata and content."""
    name: str
    description: str
    location: Path
    instructions: str
    has_tools: bool = False
    
    def __str__(self):
        return f"Skill(name='{self.name}', has_tools={self.has_tools})"

class SkillLoader:
    """Loads and manages skills from the skills directory."""
    
    def __init__(self, skills_dir: Optional[Path] = None):
        """
        Initialize the skill loader.
        
        Args:
            skills_dir: Path to skills directory (uses config default if not provided)
        """
        self.skills_dir = skills_dir or Config.SKILLS_DIRECTORY
        self.skills: Dict[str, Skill] = {}
        self._load_all_skills()
    
    def _load_all_skills(self):
        """Load all skills from the skills directory."""
        if not self.skills_dir.exists():
            logger.warning(f"Skills directory not found: {self.skills_dir}")
            self.skills_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created skills directory: {self.skills_dir}")
            return
        
        logger.info(f"Loading skills from: {self.skills_dir}")
        
        # Iterate through subdirectories in skills directory
        for skill_path in self.skills_dir.iterdir():
            if not skill_path.is_dir():
                continue
            
            skill_md = skill_path / "SKILL.md"
            if not skill_md.exists():
                logger.debug(f"Skipping {skill_path.name}: no SKILL.md found")
                continue
            
            try:
                skill = self._load_skill(skill_path)
                self.skills[skill.name] = skill
                logger.info(f"Loaded skill: {skill.name}")
            except Exception as e:
                logger.error(f"Error loading skill from {skill_path.name}: {str(e)}")
        
        logger.info(f"Total skills loaded: {len(self.skills)}")
    
    def _load_skill(self, skill_path: Path) -> Skill:
        """
        Load a single skill from a directory.
        
        Args:
            skill_path: Path to skill directory
            
        Returns:
            Skill object
        """
        skill_md = skill_path / "SKILL.md"
        
        # Read SKILL.md content
        with open(skill_md, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract description from SKILL.md (first paragraph or first 200 chars)
        description = self._extract_description(content)
        
        # Check if skill has tools.py
        has_tools = (skill_path / "tools.py").exists()
        
        skill = Skill(
            name=skill_path.name,
            description=description,
            location=skill_path,
            instructions=content,
            has_tools=has_tools
        )
        
        return skill
    
    def _extract_description(self, content: str, max_length: int = 400) -> str:
        """
        Extract description from SKILL.md content.
        
        Args:
            content: Full content of SKILL.md
            max_length: Maximum length of description
            
        Returns:
            Extracted description
        """
        # Remove markdown headers
        lines = content.split('\n')
        description_lines = []
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#'):
                description_lines.append(line)
                if len(' '.join(description_lines)) > max_length:
                    break
        
        description = ' '.join(description_lines)
        if len(description) > max_length:
            description = description[:max_length] + "..."
        
        return description or "No description available"
    
    def get_skill(self, skill_name: str) -> Optional[Skill]:
        """
        Get a skill by name.
        
        Args:
            skill_name: Name of the skill
            
        Returns:
            Skill object or None if not found
        """
        return self.skills.get(skill_name)
    
    def get_all_skills(self) -> List[Skill]:
        """
        Get all loaded skills.
        
        Returns:
            List of all skills
        """
        return list(self.skills.values())
    
    def get_skills_summary(self) -> str:
        """
        Get a formatted summary of all available skills.
        
        Returns:
            Formatted string with skills information
        """
        if not self.skills:
            return "No skills available."
        
        summary = "Available Skills:\n\n"
        for skill in self.skills.values():
            summary += f"- **{skill.name}**\n"
            summary += f"  {skill.description}\n"
            if skill.has_tools:
                summary += f"  [Has custom tools]\n"
            summary += "\n"
        
        return summary
    
    def reload_skills(self):
        """Reload all skills from the directory."""
        logger.info("Reloading skills...")
        self.skills.clear()
        self._load_all_skills()