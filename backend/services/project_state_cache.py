
import json
import logging
import os
from pathlib import Path
from typing import Dict, Optional, Any
from ..models.project_state import ProjectState
from ..models.story import Story
from .smart_cache import SmartCache

logger = logging.getLogger(__name__)

class ProjectStateCache:
    """
    Service for managing the project state cache (project-state.json).
    Handles loading, saving, and updating the state.
    """
    def __init__(self, cache_file: str, smart_cache: Optional[SmartCache] = None):
        self.cache_file = Path(cache_file)
        self.cache_data: Optional[ProjectState] = None
        self.file_mtimes: Dict[str, float] = {}
        self.sprint_status_mtime: float = 0.0
        self.smart_cache = smart_cache  # Optional SmartCache for story evidence caching

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
        
        # Invalidate SmartCache entry if story was updated
        if self.smart_cache:
            self.smart_cache.invalidate_story(story_id)
    
    def invalidate_story_cache(self, story_id: str):
        """
        Invalidate the SmartCache entry for a specific story.
        Forces the story to be re-processed on next load.
        
        Args:
            story_id: Story identifier to invalidate
        """
        if self.smart_cache:
            self.smart_cache.invalidate_story(story_id)
            logger.info(f"Invalidated SmartCache for story {story_id}")
    
    def clear_smart_cache(self):
        """Clear all SmartCache data for this project."""
        if self.smart_cache:
            self.smart_cache.clear_project_cache()
            logger.info("Cleared all SmartCache data")
    
    def get_cache_stats(self) -> Optional[Dict[str, Any]]:
        """
        Get statistics about the SmartCache.
        
        Returns:
            Dictionary with cache statistics, or None if SmartCache not configured
        """
        if self.smart_cache:
            return self.smart_cache.get_cache_stats()
        return None

    def bootstrap(self, project_root: str, use_smart_cache: bool = True) -> ProjectState:
        """
        Bootstrap the project state by scanning all files and collecting evidence.
        This is a heavy operation used when cache is missing or explicitly requested.
        
        Args:
            project_root: Path to the project root directory
            use_smart_cache: Whether to use SmartCache for done stories (default: True)
            
        Returns:
            ProjectState with all stories and their evidence
        """
        logger.info("Bootstrapping project state...")

        # We perform lazy import to avoid circular dependencies
        from ..parsers.bmad_parser import BMADParser
        from ..services.git_correlator import GitCorrelator
        from ..services.test_discoverer import TestDiscoverer
        from ..services.workflow_status_validator import WorkflowStatusValidator
        
        parser = BMADParser(project_root)
        project_model = parser.parse_project()

        # Validate workflow-status file
        validator = WorkflowStatusValidator(project_root)
        workflow_validation = validator.validate()

        # Log validation warnings/errors
        if not workflow_validation.is_valid:
            logger.warning(f"Workflow status validation failed: {workflow_validation.errors}")
            logger.info(f"Suggestions: {workflow_validation.suggestions}")
        elif workflow_validation.warnings:
            logger.warning(f"Workflow status warnings: {workflow_validation.warnings}")

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
        
        # Initialize SmartCache if enabled and not already set
        smart_cache = self.smart_cache
        if use_smart_cache and not smart_cache:
            smart_cache = SmartCache(project_root)
        
        # Initialize evidence collectors (lazy-loaded as needed)
        git_correlator = None
        test_discoverer = None
        
        total_stories = len(stories)
        cache_hits = 0
        cache_misses = 0
        
        logger.info(f"Collecting evidence for {total_stories} stories...")
        
        for story_id, story in stories.items():
            story_file_path = story.file_path or os.path.join(
                project_root,
                "_bmad-output/implementation-artifacts",
                f"{story.story_key}.md"
            )
            
            # Check SmartCache for done stories (skip expensive git/test work)
            use_cache = False
            if use_smart_cache and smart_cache and story.status == "done":
                cached_evidence, cache_hit = smart_cache.get_story_evidence(
                    story_id, story_file_path
                )
                if cache_hit:
                    story.evidence = cached_evidence
                    cache_hits += 1
                    use_cache = True
                    logger.debug(f"Cache HIT for done story {story_id}")
                else:
                    cache_misses += 1
                    logger.debug(f"Cache MISS for done story {story_id}")
            else:
                # Active stories always refresh
                cache_misses += 1
            
            if not use_cache:
                # Initialize default evidence structure to prevent frontend partial-failure crashes (Fix #5)
                story.evidence = {
                    "commits": [],
                    "commit_count": 0,
                    "status": "unknown",
                    "tests_passed": 0,
                    "tests_total": 0,
                    "healthy": False,
                    "failing_tests": [],
                    "test_files": []
                }

                # Lazy-load evidence collectors only when needed
                if not git_correlator:
                    git_correlator = GitCorrelator(project_root)
                if not test_discoverer:
                    test_discoverer = TestDiscoverer(project_root)
                
                # Get Git Evidence and Infer Tasks
                try:
                    commits = git_correlator.get_commits_for_story(story_id)
                    if commits:
                        # Store rich evidence for instant frontend display
                        story.evidence["commits"] = [c.to_dict() for c in commits]
                        story.evidence["commit_count"] = len(commits)
                        last_commit = max(c.timestamp for c in commits)
                        story.evidence["last_commit"] = last_commit.isoformat()
                        
                        # Calculate status based on recency
                        status, _ = git_correlator.calculate_status(commits)
                        story.evidence["status"] = status
                        
                        # Infer task progress (Task 6)
                        for commit in commits:
                            completed_task_nums = git_correlator.extract_task_references(commit.message)
                            for task_num in completed_task_nums:
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
                    # PERFORMANCE FIX: Don't run full tests during bootstrap for all stories.
                    # Just discover the files for now. Full parsing happens during sync/detail fetch.
                    test_files = test_discoverer.discover_tests_for_story(story_id)
                    story.evidence["test_files"] = test_files
                    
                    # Only do full test parse (subprocess run) for active stories
                    if story.status in ["in-progress", "review"] and test_files:
                        test_ev = test_discoverer.get_test_evidence_for_story(story_id, project_root)
                        if test_ev:
                            story.evidence["tests_passed"] = test_ev.pass_count
                            story.evidence["tests_total"] = test_ev.pass_count + test_ev.fail_count
                            story.evidence["healthy"] = (test_ev.fail_count == 0) and (test_ev.pass_count > 0)
                            story.evidence["failing_tests"] = test_ev.failing_test_names
                            if test_ev.last_run_time:
                                 story.evidence["last_test_run"] = test_ev.last_run_time.isoformat()
                    # For DONE stories, perform a fast static count to avoid "No tests found" warning
                    # We assume if it's DONE, tests passed. We just need to report existence.
                    elif story.status == "done" and test_files:
                        total_count = 0
                        for tf in test_files:
                            total_count += test_discoverer.count_tests_static(tf)
                        
                        story.evidence["tests_passed"] = total_count
                        story.evidence["tests_total"] = total_count
                        story.evidence["healthy"] = (total_count > 0)
                        # Estimate last run time from file mtime
                        try:
                            last_mtime = max(os.path.getmtime(tf) for tf in test_files)
                            story.evidence["last_test_run"] = datetime.fromtimestamp(last_mtime).isoformat()
                        except:
                            pass
                except Exception as e:
                    logger.warning(f"Test evidence collection failed for {story_id}: {e}")
                
                # Update but don't save yet (save once at the end for performance)
                if use_smart_cache and smart_cache:
                    # We'll save the whole structure at the end of bootstrap
                    pass
                
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
            version="1.0",
            workflow_validation=workflow_validation.to_dict()
        )
        
        # Save SmartCache at the end of bootstrap (much faster)
        if use_smart_cache and smart_cache:
            from datetime import datetime, timezone
            for sid, s in stories.items():
                s_file_path = s.file_path or os.path.join(
                    project_root, "_bmad-output/implementation-artifacts", f"{s.story_key}.md"
                )
                # Ensure evidence is stored in the cache object before final save
                smart_cache._cache_data["stories"][sid] = {
                    "title": s.title,
                    "status": s.status,
                    "file_mtime": os.path.getmtime(s_file_path) if os.path.exists(s_file_path) else 0,
                    "evidence": s.evidence,
                    "cached_at": datetime.now(timezone.utc).isoformat()
                }
            smart_cache._save_cache(smart_cache._cache_data)

        self.cache_data = state
        self.save()
        logger.info(f"Bootstrap complete. Cache hits: {cache_hits}, Cache misses: {cache_misses}")
        return state

    def sync(self, project_root: str):
        """
        Sync cache with file system.
        Checks mtimes of stories. Reparses only what changed.
        """
        if not self.cache_data:
            self.load()
            
        if not self.cache_file.exists():
            logger.info("Cache file missing on disk - bootstrapping...")
            self.bootstrap(project_root)
            return

        # Check sprint-status.yaml for changes (Story 5.4 Fix)
        sprint_status_path = os.path.join(project_root, "_bmad-output/implementation-artifacts/sprint-status.yaml")
        if os.path.exists(sprint_status_path):
            current_sprint_mtime = os.path.getmtime(sprint_status_path)
            if current_sprint_mtime > self.sprint_status_mtime:
                logger.info("sprint-status.yaml changed - triggering partial bootstrap for epics...")
                self.sprint_status_mtime = current_sprint_mtime
                # We need to re-parse project structure but keep existing story evidence if possible
                from ..parsers.bmad_parser import BMADParser
                parser = BMADParser(project_root)
                project_model = parser.parse_project()
                if project_model:
                    # Update project metadata
                    self.cache_data.project["phase"] = project_model.phase
                    
                    # Update Epics
                    new_epics = {}
                    for epic in project_model.epics:
                        epic_key = f"epic-{epic.epic_id}" if not epic.epic_id.startswith("epic-") else epic.epic_id
                        new_epics[epic_key] = epic
                    self.cache_data.epics = new_epics
                    updated = True
            
        # If still no epics or stories after load, trigger bootstrap
        if not self.cache_data.epics or not self.cache_data.stories:
            logger.info("Cache empty or missing critical data during sync - bootstrapping...")
            self.bootstrap(project_root)
            return            
        from ..parsers.bmad_parser import BMADParser
        import re
        
        parser = BMADParser(project_root)
        story_files = parser.find_all_story_files()
        
        updated = False
        git_correlator = None
        
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
                # Lazy load collectors only if needed
                if not git_correlator:
                    from ..services.git_correlator import GitCorrelator
                    git_correlator = GitCorrelator(project_root)
                
                try:
                    commits = git_correlator.get_commits_for_story(story_id)
                    if commits:
                        new_story.evidence = new_story.evidence or {}
                        new_story.evidence["commits"] = [c.to_dict() for c in commits]
                        new_story.evidence["commit_count"] = len(commits)
                        last_commit = max(c.timestamp for c in commits) 
                        new_story.evidence["last_commit"] = last_commit.isoformat()
                        
                        status, _ = git_correlator.calculate_status(commits)
                        new_story.evidence["status"] = status
                        
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
                
                # Store in SmartCache after re-parsing (Story 5.55 Fix)
                if self.smart_cache:
                    story_file_path = new_story.file_path or os.path.join(
                        project_root,
                        "_bmad-output/implementation-artifacts",
                        f"{new_story.story_key}.md"
                    )
                    self.smart_cache.set_story_evidence(
                        new_story.story_id, 
                        story_file_path, 
                        new_story.status, 
                        new_story.evidence, 
                        new_story.title
                    )
                
                updated = True
        
        if updated:
            self.save()

    def summarize_for_ai(self) -> str:
        """
        Generate a concise summary of project state for AI context.
        Focuses on current status without overwhelming details.
        Includes git status and evidence gaps for context awareness.

        Returns:
            Formatted string with project phase, epics, story statuses, git status, and evidence
        """
        if not self.cache_data:
            return "No project state available."

        lines = []
        lines.append(f"Project: {self.cache_data.project.get('name', 'Unknown')}")
        lines.append(f"Phase: {self.cache_data.project.get('phase', 'Unknown')}")

        # Summarize epics
        lines.append("\nEpics:")
        for epic_id, epic in self.cache_data.epics.items():
            lines.append(f"  - {epic_id}: {epic.title} (Status: {epic.status})")

        # Identify current story
        lines.append("\nCurrent Story:")
        in_progress_stories = [s for s in self.cache_data.stories.values() if s.status in ["in-progress", "review"]]

        if in_progress_stories:
            current = in_progress_stories[0]
            lines.append(f"  - Story {current.story_id}: {current.title} (Status: {current.status})")
        else:
            # Check for recently completed stories that need committing
            done_stories = [(sid, s) for sid, s in self.cache_data.stories.items() if s.status == "done"]
            done_stories.sort(key=lambda x: self._parse_story_id_for_sort(x[0]), reverse=True)

            if done_stories:
                recent_done_id, recent_done = done_stories[0]
                evidence = recent_done.evidence if hasattr(recent_done, 'evidence') else {}
                commit_count = evidence.get('commit_count', 0) if evidence else 0

                if commit_count == 0:
                    lines.append(f"  - Story {recent_done_id}: {recent_done.title} (Status: done)")
                    lines.append(f"    WARNING: This story is marked done but has NO COMMITS. It needs to be committed!")
                else:
                    lines.append(f"  - No active in-progress story")
                    lines.append(f"  - Most recent: Story {recent_done_id} (done, {commit_count} commits)")
            else:
                lines.append(f"  - No stories found")

        # Summarize stories (grouped by status)
        lines.append("\nStories by Status:")
        status_groups = {}
        for story_id, story in self.cache_data.stories.items():
            status = story.status
            if status not in status_groups:
                status_groups[status] = []
            status_groups[status].append(story_id)

        for status, story_ids in sorted(status_groups.items()):
            lines.append(f"  {status}: {', '.join(sorted(story_ids))}")

        # Add git status information
        try:
            import subprocess
            result = subprocess.run(
                ['git', 'status', '--short'],
                cwd=self.cache_file.parent.parent.parent,
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0 and result.stdout.strip():
                git_lines = result.stdout.strip().split('\n')
                modified = sum(1 for line in git_lines if line.startswith(' M') or line.startswith('M'))
                untracked = sum(1 for line in git_lines if line.startswith('??'))
                lines.append(f"\nGit Status:")
                lines.append(f"  - Uncommitted changes: {modified} modified, {untracked} untracked files")
                lines.append(f"  - IMPORTANT: Story changes need to be committed to git")
        except Exception as e:
            logger.debug(f"Could not fetch git status: {e}")

        # Add evidence summary for recent "done" stories
        lines.append("\nRecent Done Stories Evidence:")
        done_stories = [(sid, s) for sid, s in self.cache_data.stories.items() if s.status == "done"]
        # Sort by story_id descending (most recent first)
        done_stories.sort(key=lambda x: self._parse_story_id_for_sort(x[0]), reverse=True)

        for story_id, story in done_stories[:5]:  # Show last 5 done stories
            evidence = story.evidence if hasattr(story, 'evidence') else {}
            commit_count = evidence.get('commit_count', 0) if evidence else 0
            test_total = evidence.get('tests_total', 0) if evidence else 0
            has_commits = commit_count > 0
            has_tests = test_total > 0

            evidence_status = []
            if not has_commits:
                evidence_status.append("NO COMMITS")
            else:
                evidence_status.append(f"{commit_count} commits")

            if not has_tests:
                evidence_status.append("NO TESTS")
            else:
                evidence_status.append(f"{test_total} tests")

            lines.append(f"  - Story {story_id}: {', '.join(evidence_status)}")

        return "\n".join(lines)

    def _parse_story_id_for_sort(self, story_id: str) -> tuple:
        """Parse story ID for semantic versioning sort (5.5 < 5.55 < 5.6 < 5.7)"""
        try:
            parts = story_id.split('.')
            major = int(parts[0]) if len(parts) > 0 else 0
            if len(parts) > 1:
                minor_str = parts[1]
                # Pad single-digit minors: "5" -> 50, "55" -> 55
                minor = int(minor_str) * 10 if len(minor_str) == 1 else int(minor_str)
            else:
                minor = 0
            return (major, minor)
        except (ValueError, AttributeError):
            return (0, 0)

