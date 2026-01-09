"""
BMAD Dash - Markdown Content Parser
Parses markdown content sections from BMAD artifacts
"""
from typing import Dict, Any, List
import re


class MarkdownParser:
    """
    Parses markdown content from BMAD artifacts
    Extracts tasks, acceptance criteria, and structured content
    """
    
    @staticmethod
    def parse_content(content: str) -> Dict[str, Any]:
        """
        Extracts structured data from markdown content
        
        Args:
            content: Markdown content (after frontmatter removed)
            
        Returns:
            Dictionary with keys:
            - 'tasks': List of Task dicts with {'title', 'status', 'subtasks'}
            - 'acceptance_criteria': List of acceptance criteria strings
            - 'headings': List of heading dicts with {'level', 'text', 'line'}
        """
        if not content:
            return {
                "tasks": [],
                "acceptance_criteria": [],
                "headings": []
            }
        
        tasks = MarkdownParser._extract_tasks(content)
        acceptance_criteria = MarkdownParser._extract_acceptance_criteria(content)
        headings = MarkdownParser._extract_headings(content)
        
        return {
            "tasks": tasks,
            "acceptance_criteria": acceptance_criteria,
            "headings": headings
        }
    
    @staticmethod
    def _extract_tasks(content: str) -> List[Dict[str, Any]]:
        """
        Extract tasks from markdown content
        Supports:
        - [ ] Unchecked task
        - [x] Checked task
        - Nested subtasks (indented)
        """
        tasks = []
        lines = content.split('\n')
        current_task = None
        task_counter = 1
        
        for i, line in enumerate(lines):
            # Match top-level tasks (must start at beginning of line - no leading whitespace)
            # Use raw line, not stripped
            task_match = re.match(r'^[-*]\s+\[([ xX])\]\s+(.+)$', line)
            
            if task_match:
                # Save previous task if exists
                if current_task:
                    tasks.append(current_task)
                    task_counter += 1
                
                # Create new task
                status = 'done' if task_match.group(1).lower() == 'x' else 'todo'
                title = task_match.group(2).strip()
                
                current_task = {
                    "task_id": f"task-{task_counter}",
                    "title": title,
                    "status": status,
                    "subtasks": []
                }
            
            # Match subtasks (indented with spaces or tabs)
            elif current_task:
                subtask_match = re.match(r'^\s+[-*]\s+\[([ xX])\]\s+(.+)$', line)
                if subtask_match:
                    subtask_status = 'done' if subtask_match.group(1).lower() == 'x' else 'todo'
                    subtask_text = subtask_match.group(2).strip()
                    current_task["subtasks"].append({
                        "text": subtask_text,
                        "status": subtask_status
                    })

        
        # Don't forget the last task
        if current_task:
            tasks.append(current_task)
        
        return tasks
    
    @staticmethod
    def _extract_acceptance_criteria(content: str) -> List[str]:
        """
        Extract acceptance criteria from markdown content
        Looks for "Acceptance Criteria" section and extracts bullet points
        """
        criteria = []
        lines = content.split('\n')
        in_criteria_section = False
        
        for line in lines:
            # Check if we're entering the Acceptance Criteria section
            if re.match(r'^#+\s*Acceptance\s+Criteria', line, re.IGNORECASE):
                in_criteria_section = True
                continue
            
            # Check if we've hit another section
            if in_criteria_section and re.match(r'^#+\s+', line):
                in_criteria_section = False
                continue
            
            # Extract criteria (starts with Given/When/Then/And or bullet points)
            if in_criteria_section:
                # Match Given/When/Then/And patterns
                criteria_match = re.match(r'^\*\*(?:Given|When|Then|And)\*\*\s+(.+)$', line.strip())
                if criteria_match:
                    criteria.append(line.strip())
                # Also match plain bullet points
                elif re.match(r'^[-*]\s+', line.strip()):
                    criteria.append(line.strip())
        
        return criteria
    
    @staticmethod
    def _extract_headings(content: str) -> List[Dict[str, Any]]:
        """
        Extract all markdown headings for structure tracking
        """
        headings = []
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            heading_match = re.match(r'^(#{1,6})\s+(.+)$', line)
            if heading_match:
                level = len(heading_match.group(1))
                text = heading_match.group(2).strip()
                headings.append({
                    "level": level,
                    "text": text,
                    "line": line_num
                })
        
        return headings

