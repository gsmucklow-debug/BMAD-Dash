"""
BMAD Dash - Main BMAD Artifact Parser
Coordinates parsing of BMAD artifacts (epics, stories, sprint-status)
"""
import os
import glob
from typing import Optional
from ..models.project import Project
from ..models.epic import Epic
from ..models.story import Story
from ..models.task import Task
from .yaml_parser import YAMLParser
from .markdown_parser import MarkdownParser
from ..services.phase_detector import PhaseDetector
from ..utils.cache import Cache


class BMADParser:
    """
    Main parser for BMAD artifacts
    Orchestrates parsing of sprint-status, story files, and builds Project model
    """
    
    def __init__(self, root_path: str):
        """
        Initialize parser with project root path
        
        Args:
            root_path: Path to project root directory
        """
        self.root_path = root_path
        self.cache = Cache()
        
        # Define artifact paths
        self.bmad_output = os.path.join(root_path, "_bmad-output")
        self.implementation_artifacts = os.path.join(self.bmad_output, "implementation-artifacts")
        self.planning_artifacts = os.path.join(self.bmad_output, "planning-artifacts")
    
    def parse_project(self) -> Optional[Project]:
        """
        Parses all BMAD artifacts and returns complete Project structure
        
        Returns:
            Project dataclass with all epics, stories, and tasks populated
            Returns None if essential files are missing
        """
        # Detect project phase
        phase = PhaseDetector.detect_phase(self.root_path)
        
        # Extract project name from root path
        project_name = os.path.basename(self.root_path)
        
        # Parse sprint-status.yaml if it exists
        sprint_status_path = os.path.join(self.implementation_artifacts, "sprint-status.yaml")
        sprint_status_mtime = 0.0
        epics = []
        
        if os.path.exists(sprint_status_path):
            sprint_status_mtime = os.path.getmtime(sprint_status_path)
            
            # Try to get from cache
            cache_key = f"sprint_status_{self.root_path}"
            cached = self.cache.get(cache_key, sprint_status_path)
            
            if cached:
                epics = cached
            else:
                # Parse sprint-status.yaml
                with open(sprint_status_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                parsed = YAMLParser.parse_yaml_file(content, sprint_status_path)
                
                if 'error' not in parsed:
                    # Handle flat development_status format
                    dev_status = parsed.get('development_status', {})
                    if dev_status:
                        epics = self._parse_development_status(dev_status)
                    else:
                        # Fallback to nested epics format
                        epics_data = parsed.get('epics', [])
                        for epic_data in epics_data:
                            epic = self._build_epic(epic_data)
                            if epic:
                                epics.append(epic)
                    
                    self.cache.set(cache_key, epics, sprint_status_path)
        
        # Create and return Project
        project = Project(
            name=project_name,
            phase=phase,
            root_path=self.root_path,
            epics=epics,
            sprint_status_mtime=sprint_status_mtime
        )
        
        return project
    
    def _parse_development_status(self, dev_status: dict) -> list:
        """
        Parse flat development_status format into Epic/Story structure
        
        Format:
            epic-0: in-progress
            0-1-story-name: done
            epic-1: backlog
            1-1-another-story: in-progress
        
        Args:
            dev_status: Dictionary from development_status key
            
        Returns:
            List of Epic dataclasses
        """
        import re
        
        # Group entries by epic
        epic_map = {}  # epic_num -> {status, stories: []}
        
        for key, status in dev_status.items():
            # Skip retrospective entries
            if 'retrospective' in key:
                continue
            
            # Check if this is an epic entry (e.g., "epic-0")
            epic_match = re.match(r'^epic-(\d+)$', key)
            if epic_match:
                epic_num = int(epic_match.group(1))
                if epic_num not in epic_map:
                    epic_map[epic_num] = {'status': status, 'stories': []}
                else:
                    epic_map[epic_num]['status'] = status
                continue
            
            # Check if this is a story entry (e.g., "2-4-evidence-badges")
            story_match = re.match(r'^(\d+)-(\d+)-(.+)$', key)
            if story_match:
                epic_num = int(story_match.group(1))
                story_num = int(story_match.group(2))
                story_slug = story_match.group(3)
                
                if epic_num not in epic_map:
                    epic_map[epic_num] = {'status': 'backlog', 'stories': []}
                
                epic_map[epic_num]['stories'].append({
                    'story_key': key,
                    'story_id': f"{epic_num}.{story_num}",
                    'epic': epic_num,
                    'status': status,
                    'title': story_slug.replace('-', ' ').title()
                })
        
        # Build Epic objects
        epics = []
        for epic_num in sorted(epic_map.keys()):
            epic_data = epic_map[epic_num]
            
            # Parse story files
            stories = []
            for story_data in epic_data['stories']:
                story = self._parse_story_file(story_data)
                if story:
                    stories.append(story)
            
            # Calculate progress
            total_stories = len(stories)
            done_stories = sum(1 for s in stories if s.status == 'done')
            
            epic = Epic(
                epic_id=str(epic_num),
                title=f"Epic {epic_num}",
                status=epic_data['status'],
                stories=stories,
                progress={"total": total_stories, "done": done_stories}
            )
            epics.append(epic)
        
        return epics
    
    def _build_epic(self, epic_data: dict) -> Optional[Epic]:
        """
        Build Epic dataclass from sprint-status epic data
        
        Args:
            epic_data: Epic dict from sprint-status.yaml
            
        Returns:
            Epic dataclass with populated stories
        """
        epic_id = str(epic_data.get('epic_id', epic_data.get('id', '')))
        title = epic_data.get('title', 'Untitled Epic')
        status = epic_data.get('status', 'backlog')
        stories_data = epic_data.get('stories', [])
        
        # Parse story files for this epic
        stories = []
        for story_data in stories_data:
            story = self._parse_story_file(story_data)
            if story:
                stories.append(story)
        
        # Calculate progress
        total_stories = len(stories)
        done_stories = sum(1 for s in stories if s.status == 'done')
        progress = {
            "total": total_stories,
            "done": done_stories
        }
        
        epic = Epic(
            epic_id=epic_id,
            title=title,
            status=status,
            stories=stories,
            progress=progress
        )
        
        return epic
    
    def _parse_story_file(self, story_data: dict) -> Optional[Story]:
        """
        Parse a story markdown file
        
        Args:
            story_data: Story dict from sprint-status.yaml with 'story_key'
            
        Returns:
            Story dataclass with parsed content and tasks
        """
        story_key = story_data.get('story_key', '')
        if not story_key:
            return None
        
        # Find story file
        story_filename = f"{story_key}.md"
        story_path = os.path.join(self.implementation_artifacts, story_filename)
        
        if not os.path.exists(story_path):
            # Story file missing, return minimal Story object
            return Story(
                story_id=story_data.get('story_id', ''),
                story_key=story_key,
                title=story_data.get('title', 'Untitled Story'),
                status=story_data.get('status', 'backlog'),
                epic=story_data.get('epic', 0),
                tasks=[],
                created="",
                completed=None,
                file_path="",
                mtime=0.0
            )
        
        # Get file mtime
        mtime = os.path.getmtime(story_path)
        
        # Try cache
        cache_key = f"story_{story_key}"
        cached = self.cache.get(cache_key, story_path)
        
        if cached:
            return cached
        
        # Parse story file
        try:
            with open(story_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse frontmatter
            parsed = YAMLParser.parse_frontmatter(content, story_path)
            frontmatter = parsed.get('frontmatter', {})
            markdown_content = parsed.get('content', '')
            
            # Parse markdown content for tasks
            markdown_data = MarkdownParser.parse_content(markdown_content)
            task_dicts = markdown_data.get('tasks', [])
            
            # Convert task dicts to Task dataclasses
            tasks = [Task.from_dict(t) for t in task_dicts]
            
            # Build Story
            story = Story(
                story_id=frontmatter.get('story_id', story_data.get('story_id', '')),
                story_key=frontmatter.get('story_key', story_key),
                title=frontmatter.get('title', story_data.get('title', 'Untitled Story')),
                status=frontmatter.get('status', story_data.get('status', 'backlog')),
                epic=frontmatter.get('epic', story_data.get('epic', 0)),
                tasks=tasks,
                created=frontmatter.get('created', ''),
                completed=frontmatter.get('completed'),
                file_path=story_path,
                mtime=mtime
            )
            
            # Cache the story
            self.cache.set(cache_key, story, story_path)
            
            return story
            
        except Exception as e:
            # Error parsing story file, return minimal Story
            print(f"Error parsing story file {story_path}: {e}")
            return Story(
                story_id=story_data.get('story_id', ''),
                story_key=story_key,
                title=story_data.get('title', 'Untitled Story'),
                status=story_data.get('status', 'backlog'),
                epic=story_data.get('epic', 0),
                tasks=[],
                created="",
                completed=None,
                file_path=story_path,
                mtime=mtime
            )
    
    def find_all_story_files(self) -> list:
        """
        Find all story markdown files in implementation-artifacts directory
        
        Returns:
            List of story file paths
        """
        if not os.path.exists(self.implementation_artifacts):
            return []
        
        # Pattern: X-Y-story-name.md where X is epic and Y is story number
        pattern = os.path.join(self.implementation_artifacts, "*-*-*.md")
        story_files = glob.glob(pattern)
        
        return story_files
    
    def invalidate_cache(self):
        """Invalidate all cached data"""
        self.cache.invalidate_all()

