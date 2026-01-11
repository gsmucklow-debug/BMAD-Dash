
import json
import logging
import os
from pathlib import Path
from typing import Dict, Optional, Any
from ..models.project_state import ProjectState
from ..models.story import Story

logger = logging.getLogger(__name__)

class ProjectStateCache:
    """
    Service for managing the project state cache (project-state.json).
    Handles loading, saving, and updating the state.
    """
    def __init__(self, cache_file: str):
        self.cache_file = Path(cache_file)
        self.cache_data: Optional[ProjectState] = None
        self.file_mtimes: Dict[str, float] = {}

    def load(self) -> ProjectState:
        """
        Load project state from cache file.
        If file is missing or invalid, initializes a new empty state.
        """
        if not self.cache_file.exists():
            logger.info(f"Cache file {self.cache_file} not found. Creating new.")
            self.cache_data = ProjectState(
                project={"name": "BMAD Dash", "bmad_version": "latest"},
                current={},
                epics={},
                stories={}
            )
            self.save()
            return self.cache_data
        
        try:
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.cache_data = ProjectState.from_dict(data)
                return self.cache_data
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Error loading cache: {e}")
            # Fallback to empty state
            self.cache_data = ProjectState(
                project={"name": "BMAD Dash", "bmad_version": "latest"},
                current={},
                epics={},
                stories={}
            )
            return self.cache_data

    def save(self):
        """Save current cache state to disk"""
        if not self.cache_data:
            return
            
        # Ensure directory exists
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)
            
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache_data.to_dict(), f, indent=2)
        except IOError as e:
            logger.error(f"Error saving cache: {e}")

    def get_story(self, story_id: str) -> Optional[Story]:
        """Get a story by ID from the cache"""
        if not self.cache_data:
            self.load()
        if self.cache_data and self.cache_data.stories:
            return self.cache_data.stories.get(story_id)
        return None

    def update_story(self, story_id: str, data: Dict[str, Any]):
        """
        Update a story with partial data.
        Merges existing story data with provided updates.
        """
        story = self.get_story(story_id)
        if not story:
            logger.warning(f"Story {story_id} not found in cache. Cannot update.")
            return
            
        # Update attributes
        for k, v in data.items():
            if hasattr(story, k):
                setattr(story, k, v)
        
        # Save changes
        self.save()

    def bootstrap(self, project_root: str) -> ProjectState:
        """
        Bootstrap the project state by scanning all files and collecting evidence.
        This is a heavy operation used when cache is missing or explicitly requested.
        """
        logger.info("Bootstrapping project state...")
        
        # We perform lazy import to avoid circular dependencies
        from ..parsers.bmad_parser import BMADParser
        from ..services.git_correlator import GitCorrelator
        from ..services.test_discoverer import TestDiscoverer
        
        parser = BMADParser(project_root)
        project_model = parser.parse_project()
        
        epics = {}
        stories = {}
        
        # Populate epics and stories from parser result
        if project_model:
            for epic in project_model.epics:
                # Use "epic-{id}" format for consistency with story.epic references
                epic_key = f"epic-{epic.epic_id}" if not epic.epic_id.startswith("epic-") else epic.epic_id
                epics[epic_key] = epic
                for story in epic.stories:
                    stories[story.story_id] = story
        
        # Initialize evidence collectors
        git_correlator = GitCorrelator(project_root)
        test_discoverer = TestDiscoverer(project_root)
        
        total_stories = len(stories)
        logger.info(f"Collecting evidence for {total_stories} stories...")
        
        for story_id, story in stories.items():
            # Get Git Evidence and Infer Tasks
            try:
                commits = git_correlator.get_commits_for_story(story_id)
                if commits:
                    story.evidence["commits"] = len(commits)
                    # get max timestamp
                    last_commit = max(c.timestamp for c in commits) 
                    story.evidence["last_commit"] = last_commit.isoformat()
                    
                    # Infer task progress (Task 6)
                    # Iterate commits to find task completion evidence
                    for commit in commits:
                        completed_task_nums = git_correlator.extract_task_references(commit.message)
                        for task_num in completed_task_nums:
                            # Find task (assuming ID matches number string)
                            # Task IDs are usually "1", "2" etc.
                            task_str_id = str(task_num)
                            for task in story.tasks:
                                if task.task_id == task_str_id and task.status != "done":
                                    task.status = "done"
                                    task.inferred = True
                                    logger.info(f"Inferred task {task_str_id} done for story {story_id} from commit")
            except Exception as e:
                logger.warning(f"Git evidence collection failed for {story_id}: {e}")
                
            # Get Test Evidence
            try:
                test_ev = test_discoverer.get_test_evidence_for_story(story_id, project_root)
                if test_ev:
                    story.evidence["tests_passed"] = test_ev.pass_count
                    story.evidence["tests_total"] = test_ev.pass_count + test_ev.fail_count
                    story.evidence["healthy"] = (test_ev.fail_count == 0) and (test_ev.pass_count > 0)
                    if test_ev.last_run_time:
                         story.evidence["last_test_run"] = test_ev.last_run_time.isoformat()
            except Exception as e:
                logger.warning(f"Test evidence collection failed for {story_id}: {e}")
                
        # Create State
        # Infer current story? For now leaving empty or simple
        state = ProjectState(
            project={
                "name": project_model.name if project_model else "BMAD Dash",
                "bmad_version": "latest",
                "phase": project_model.phase if project_model else "Implementation",
                "root": project_root
            },
            current={}, 
            epics=epics,
            stories=stories,
            version="1.0"
        )
        
        self.cache_data = state
        self.save()
        logger.info("Bootstrap complete.")
        return state

    def sync(self, project_root: str):
        """
        Sync cache with file system.
        Checks mtimes of stories. Reparses only what changed.
        """
        if not self.cache_data:
            self.load()
            
        from ..parsers.bmad_parser import BMADParser
        import re
        
        parser = BMADParser(project_root)
        story_files = parser.find_all_story_files()
        
        updated = False
        
        for file_path in story_files:
            try:
                mtime = os.path.getmtime(file_path)
            except OSError:
                continue
                
            filename = os.path.basename(file_path)
            story_key = filename.replace('.md', '')
            
            # Extract story_id from key (e.g., "5-4-name" -> "5.4")
            match = re.match(r'^(\d+)-(\d+)-', story_key)
            if not match:
                continue
            
            story_id = f"{match.group(1)}.{match.group(2)}"
            
            # Check cache
            cached_story = self.cache_data.stories.get(story_id)
            
            if cached_story:
                # Compare mtime (float comparison with epsilon)
                # mtime can be float, give some buffer
                if abs(cached_story.mtime - mtime) < 0.5:
                    continue
            
            # Reparse
            logger.info(f"Story {story_id} changed. Reparsing...")
            new_story = parser.parse_story(story_key)
            
            if new_story:
                # Re-run evidence collection and inference for the changed story
                # We do this because file changes might invalidate previous inference 
                # or we might want new evidence status
                from ..services.git_correlator import GitCorrelator
                git_correlator = GitCorrelator(project_root) # Optimized init
                
                try:
                    commits = git_correlator.get_commits_for_story(story_id)
                    if commits:
                        new_story.evidence = new_story.evidence or {} # Ensure dict
                        new_story.evidence["commits"] = len(commits)
                        last_commit = max(c.timestamp for c in commits) 
                        new_story.evidence["last_commit"] = last_commit.isoformat()
                        
                        # Infer task progress
                        for commit in commits:
                            completed_task_nums = git_correlator.extract_task_references(commit.message)
                            for task_num in completed_task_nums:
                                task_str_id = str(task_num)
                                for task in new_story.tasks:
                                    if task.task_id == task_str_id and task.status != "done":
                                        task.status = "done"
                                        task.inferred = True
                except Exception as e:
                    logger.warning(f"Git evidence collection failed for {story_id} during sync: {e}")
                
                 # Preserve test evidence (expensive to re-run?) 
                 # Or maybe re-run it? For now, we'll preserve unless we implement TestDiscoverer in sync
                if cached_story and hasattr(cached_story, 'evidence'):
                     # Merge tests evidence if not present (simple approach)
                     for k, v in cached_story.evidence.items():
                         if k.startswith("tests") and k not in new_story.evidence:
                             new_story.evidence[k] = v

                self.cache_data.stories[new_story.story_id] = new_story
                updated = True
        
        if updated:
            self.save()

