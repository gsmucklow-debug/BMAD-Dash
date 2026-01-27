"""
BMAD Dash - Main BMAD Artifact Parser
Coordinates parsing of BMAD artifacts (epics, stories, sprint-status)
"""
import os
import glob
import re
from typing import Optional
from ..models.project import Project
from ..models.epic import Epic
from ..models.story import Story
from ..models.task import Task
from .yaml_parser import YAMLParser
from .markdown_parser import MarkdownParser
from ..services.phase_detector import PhaseDetector
from ..services.git_correlator import GitCorrelator
from ..utils.cache import Cache


# Gap severity constants
GAP_SEVERITY_HIGH = 'high'
GAP_SEVERITY_MEDIUM = 'medium'
GAP_SEVERITY_LOW = 'low'


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
    
    def parse_story(self, story_key: str) -> Optional[Story]:
        """
        Parse a single story by key
        
        Args:
            story_key: Story key (e.g. "1-1-story-name")
            
        Returns:
            Story object or None
        """
        return self._parse_story_file({'story_key': story_key})

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
                mtime=0.0,
                workflow_history=[],
                gaps=[]
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
            
            # Extract workflow history from frontmatter (with Git fallback)
            workflow_history = self._extract_workflow_history(
                frontmatter,
                story_data.get('story_id'),
                story_path
            )
            
            # Detect gaps
            gaps = self._detect_gaps(frontmatter, workflow_history, story_path)
            
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
                mtime=mtime,
                workflow_history=workflow_history,
                gaps=gaps,
                last_updated=frontmatter.get('last_updated')
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
                mtime=mtime,
                workflow_history=[],
                gaps=[]
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
    
    def _extract_workflow_history(self, frontmatter: dict, story_id: str = None, story_path: str = None) -> list:
        """
        Extract workflow history from story frontmatter
        Falls back to Git commit message analysis if frontmatter history is missing

        Args:
            frontmatter: Parsed YAML frontmatter dictionary
            story_id: Story identifier (e.g., "1.3") for Git fallback
            story_path: Path to story file for Git fallback

        Returns:
            List of workflow execution records, sorted by timestamp (most recent first)
        """
        workflows = frontmatter.get('workflow_history', [])
        
        # If workflows is a list of dicts, return directly (sorted)
        if isinstance(workflows, list) and workflows:
            # Sort by timestamp (most recent first)
            sorted_workflows = sorted(
                workflows,
                key=lambda x: x.get('timestamp', ''),
                reverse=True
            )
            return sorted_workflows
        
        # Fallback 1: Check for code-review-*.md files
        # This handles retroactive reviews where workflow_history wasn't added to frontmatter
        if story_id and self.root_path:
            try:
                code_review_workflows = self._detect_code_review_files(story_id)
                if code_review_workflows:
                    return code_review_workflows
            except Exception as e:
                print(f"Warning: Code review file detection failed for story {story_id}: {e}")

        # Fallback 2: Extract workflow history from Git commit messages
        # This happens when frontmatter workflows is missing or empty
        if story_id and self.root_path:
            try:
                git_history = self._extract_workflow_history_from_git(story_id)
                if git_history:
                    return git_history
            except Exception as e:
                # Log but don't fail - just return empty list
                print(f"Warning: Git fallback failed for story {story_id}: {e}")

        # If workflows is None or not found, return empty list
        return []

    def _detect_code_review_files(self, story_id: str) -> list:
        """
        Detect workflow execution by checking for code-review-*.md files
        Handles retroactive reviews where workflow_history wasn't added to frontmatter

        Args:
            story_id: Story identifier (e.g., "1.3")

        Returns:
            List of workflow execution records inferred from code review files
        """
        try:
            import os
            import yaml
            from pathlib import Path

            # Convert story_id to file pattern (e.g., "1.3" -> "code-review-1-3.md")
            story_file_id = story_id.replace('.', '-')
            code_review_pattern = f"code-review-{story_file_id}.md"

            # Look for code review file in implementation-artifacts
            artifacts_dir = os.path.join(self.root_path, '_bmad-output', 'implementation-artifacts')
            code_review_path = os.path.join(artifacts_dir, code_review_pattern)

            workflows = []

            # Check if code review file exists
            if os.path.exists(code_review_path):
                # Parse the code review file to get metadata
                with open(code_review_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                review_date = ''
                review_exists = True  # Presence of file indicates review was done

                # Try to extract YAML frontmatter if it exists
                if content.startswith('---'):
                    parts = content.split('---', 2)
                    if len(parts) >= 3:
                        try:
                            metadata = yaml.safe_load(parts[1])
                            review_date = metadata.get('date', '')
                        except yaml.YAMLError as e:
                            print(f"Warning: Failed to parse code review YAML for {story_id}: {e}")

                # If no date in YAML, try to extract from content
                if not review_date:
                    # Look for patterns like "Date: 2026-01-10" or "Review Date: 2026-01-10"
                    import re
                    date_match = re.search(r'[Dd]ate[:\s]+(\d{4}-\d{2}-\d{2})', content)
                    if date_match:
                        review_date = date_match.group(1)

                # If code review file exists, infer both workflows were completed
                # (presence of the file indicates the review happened)
                if review_exists:
                    # Add dev-story workflow (must have been done before review)
                    workflows.append({
                        'name': 'dev-story',
                        'workflow': 'bmad-bmm-workflows-dev-story',
                        'status': 'done',
                        'date': review_date,
                        'source': 'inferred-from-code-review-file'
                    })

                    # Add code-review workflow
                    workflows.append({
                        'name': 'code-review',
                        'workflow': 'bmad-bmm-workflows-code-review',
                        'status': 'done',
                        'date': review_date,
                        'source': 'inferred-from-code-review-file'
                    })

            return workflows

        except Exception as e:
            print(f"Error detecting code review files for {story_id}: {e}")
            return []

    def _extract_workflow_history_from_git(self, story_id: str) -> list:
        """
        Extract workflow history from Git commit messages
        Analyzes commit messages to identify workflow executions
        
        Args:
            story_id: Story identifier (e.g., "1.3")
            
        Returns:
            List of workflow execution records extracted from Git commits
        """
        try:
            correlator = GitCorrelator(self.root_path)
            commits = correlator.get_commits_for_story(story_id)
            
            if not commits:
                return []
            
            # Parse commit messages to extract workflow information
            workflow_history = []
            workflow_patterns = {
                'dev-story': re.compile(r'dev[-_]story|development', re.IGNORECASE),
                'code-review': re.compile(r'code[-_]review|review', re.IGNORECASE),
                'test': re.compile(r'test|testing|test[-_]evidence', re.IGNORECASE),
                'create-story': re.compile(r'create[-_]story|story[-_]created', re.IGNORECASE)
            }
            
            for commit in commits:
                message = commit.message.lower()
                detected_workflow = None
                
                # Check for workflow keywords in commit message
                for workflow_name, pattern in workflow_patterns.items():
                    if pattern.search(message):
                        detected_workflow = workflow_name
                        break
                
                if detected_workflow:
                    # Determine result from commit message
                    result = 'success'
                    if any(word in message for word in ['fail', 'error', 'fix', 'bug']):
                        result = 'failure'
                    elif any(word in message for word in ['skip', 'wip', 'incomplete']):
                        result = 'skipped'
                    
                    workflow_entry = {
                        'name': detected_workflow,
                        'timestamp': commit.timestamp.isoformat() if commit.timestamp else None,
                        'result': result,
                        'git_commit': commit.sha[:8],  # Short SHA
                        'source': 'git'  # Indicate this came from Git analysis
                    }
                    workflow_history.append(workflow_entry)
            
            # Sort by timestamp (most recent first)
            workflow_history.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            
            return workflow_history
            
        except Exception as e:
            print(f"Error extracting workflow history from Git: {e}")
            return []
    
    def _detect_gaps(self, frontmatter: dict, workflow_history: list, story_path: str = None) -> list:
        """
        Detect workflow gaps based on story status and workflow history
        
        Gap Detection Rules:
        1. Story is "done" but no "dev-story" workflow was run
        2. "dev-story" is complete but no "code-review" was executed
        3. "code-review" is done but 0 passing tests found (test-gap)
        
        Args:
            frontmatter: Parsed YAML frontmatter dictionary
            workflow_history: List of workflow execution records
            story_path: Path to story file for test evidence lookup
            
        Returns:
            List of gap dictionaries with type, message, and suggested command
        """
        gaps = []
        status = frontmatter.get('status', '')
        
        # Create a set of workflow names for quick lookup
        executed_workflows = set()
        for wf in workflow_history:
            if isinstance(wf, dict):
                # Handle dict entries (from frontmatter or git logs)
                wf_name = wf.get('name') or wf.get('workflow') or ''
            elif isinstance(wf, str):
                # Handle string entries
                wf_name = wf
            else:
                wf_name = ''
            
            if wf_name:
                # Normalize: remove 'bmad-bmm-workflows-' prefix if present
                clean_name = wf_name.replace('bmad-bmm-workflows-', '')
                executed_workflows.add(clean_name)
        
        # Gap 1: Story is "done" but no "dev-story" workflow was run
        if status == 'done' and 'dev-story' not in executed_workflows:
            gaps.append({
                'type': 'missing-dev-story',
                'message': '⚠️ Missing: dev-story workflow',
                'suggested_command': 'npx bmad-method run dev-story',
                'severity': GAP_SEVERITY_HIGH
            })
        
        # Gap 2: "dev-story" is complete but no "code-review" was executed
        if 'dev-story' in executed_workflows and 'code-review' not in executed_workflows:
            gaps.append({
                'type': 'missing-code-review',
                'message': '⚠️ Missing: code-review workflow',
                'suggested_command': 'npx bmad-method run code-review',
                'severity': GAP_SEVERITY_MEDIUM
            })
        
        # Gap 3: "code-review" is done but 0 passing tests found (test-gap)
        # This requires actual test evidence verification
        if status == 'done' and 'code-review' in executed_workflows:
            # Check test evidence to verify if 0 tests are passing
            test_gap_detected = self._check_test_gap(story_path)
            
            if test_gap_detected:
                gaps.append({
                    'type': 'test-gap',
                    'message': '⚠️ Critical: No passing tests found',
                    'suggested_command': 'npx bmad-method run dev-story',
                    'severity': GAP_SEVERITY_HIGH
                })
        
        return gaps
    
    def _check_test_gap(self, story_path: str = None) -> bool:
        """
        Check if there are 0 passing tests for the story
        
        Args:
            story_path: Path to story file
            
        Returns:
            True if 0 passing tests detected, False otherwise
        """
        if not story_path:
            return False
        
        try:
            # Import test discovery service
            from ..services.test_discoverer import TestDiscoverer
            from ..utils.story_test_parser import parse_test_counts_from_story_file

            # Extract story ID from story path
            story_id = None
            match = re.search(r'(\d+)-(\d+)-', story_path)
            if match:
                story_id = f"{match.group(1)}.{match.group(2)}"

            if not story_id:
                return False

            # Discover test files for this story
            discoverer = TestDiscoverer(self.root_path)
            test_files = discoverer.discover_tests_for_story(story_id)

            # If test files found, count tests
            if test_files:
                # Use static count for gap detection to avoid running tests during parse
                total_tests = 0
                for tf in test_files:
                    total_tests += discoverer.count_tests_static(tf)

                # Return True if 0 tests are found
                return total_tests == 0

            # No test files found - check for manual test evidence in story file
            manual_counts = parse_test_counts_from_story_file(story_id, self.root_path)
            if manual_counts and manual_counts.get('total_tests', 0) > 0:
                # Manual test evidence found - no gap
                return False

            # No test files AND no manual evidence - this is a gap
            return True
            
        except Exception as e:
            # If we can't check test evidence, don't add a gap
            # (better to have false negative than false positive)
            print(f"Warning: Could not check test gap for {story_path}: {e}")
            return False
    
    def invalidate_cache(self):
        """Invalidate all cached data"""
        self.cache.invalidate_all()

