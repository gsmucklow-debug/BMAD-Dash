"""
BMAD Dash - YAML Frontmatter Parser
Extracts YAML frontmatter from markdown files
"""
import yaml
from typing import Dict, Any, Tuple
import re


class YAMLParser:
    """
    Parses YAML frontmatter from markdown files
    Handles both standalone YAML files and markdown files with frontmatter
    """
    
    @staticmethod
    def parse_frontmatter(content: str, filepath: str = "") -> Dict[str, Any]:
        """
        Extracts YAML frontmatter from markdown content
        
        Args:
            content: File content (may be pure YAML or markdown with frontmatter)
            filepath: Path to file for error reporting
            
        Returns:
            Dictionary with keys:
            - 'frontmatter': Parsed YAML data (dict)
            - 'content': Remaining markdown content after frontmatter
            - 'error': Error message if parsing failed (optional)
        """
        if not content or not content.strip():
            return {
                "frontmatter": {},
                "content": ""
            }
        
        # Check if this is a pure YAML file (like sprint-status.yaml)
        if not content.strip().startswith("---"):
            # Try parsing as pure YAML
            try:
                parsed = yaml.safe_load(content)
                return {
                    "frontmatter": parsed if isinstance(parsed, dict) else {},
                    "content": ""
                }
            except yaml.YAMLError as e:
                return {
                    "frontmatter": {},
                    "content": content,
                    "error": f"Malformed YAML in {filepath}: {str(e)}"
                }
        
        # Parse markdown with YAML frontmatter
        # Pattern: starts with ---, YAML content, ends with ---
        pattern = r'^---\s*\n(.*?)\n---\s*\n(.*)$'
        match = re.match(pattern, content, re.DOTALL)
        
        if not match:
            # Missing closing delimiter
            return {
                "frontmatter": {},
                "content": content,
                "error": f"Malformed YAML frontmatter in {filepath}: Missing closing '---' delimiter"
            }
        
        yaml_content = match.group(1)
        markdown_content = match.group(2)
        
        try:
            frontmatter = yaml.safe_load(yaml_content)
            return {
                "frontmatter": frontmatter if isinstance(frontmatter, dict) else {},
                "content": markdown_content
            }
        except yaml.YAMLError as e:
            return {
                "frontmatter": {},
                "content": content,
                "error": f"Malformed YAML in {filepath}: {str(e)}"
            }
    
    @staticmethod
    def parse_yaml_file(content: str, filepath: str = "") -> Dict[str, Any]:
        """
        Parse a pure YAML file (no frontmatter delimiters)
        
        Args:
            content: YAML file content
            filepath: Path to file for error reporting
            
        Returns:
            Parsed YAML dict or error dict
        """
        try:
            parsed = yaml.safe_load(content)
            return parsed if isinstance(parsed, dict) else {}
        except yaml.YAMLError as e:
            return {
                "error": f"Malformed YAML in {filepath}: {str(e)}"
            }

