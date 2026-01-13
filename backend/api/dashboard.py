"""
BMAD Dash - Dashboard API Endpoint
GET /api/dashboard - Returns project overview with epics and stories
Story 5.55: Smart Per-Project Cache Layer
"""
from flask import Blueprint, jsonify, request
import os
import logging
from typing import Optional, Dict, Any, List
from ..parsers.bmad_parser import BMADParser
from ..utils.error_handler import handle_api_errors
from ..utils.cache import Cache

logger = logging.getLogger(__name__)

dashboard_bp = Blueprint('dashboard', __name__)

# Global cache instance
_cache = Cache()


from ..services.project_state_cache import ProjectStateCache
from ..services.smart_cache import SmartCache
from ..models.project import Project
import time

@dashboard_bp.route('/api/dashboard', methods=['GET'])
@handle_api_errors
def get_dashboard():
    """
    Returns dashboard data including project overview, breadcrumb, quick_glance, and kanban
    Using ProjectStateCache for performance (Story 5.4)
    """
    # Extract and validate project_root parameter
    project_root = request.args.get('project_root')
    
    if not project_root:
        raise ValueError("project_root parameter is required")
    
    if not os.path.exists(project_root):
        raise FileNotFoundError(f"Project not found: {project_root}")
    
    # Initialize SmartCache for evidence caching (Story 5.55)
    smart_cache = SmartCache(project_root)
    
    # Initialize cache service with SmartCache
    cache_file = os.path.join(project_root, "_bmad-output/implementation-artifacts/project-state.json")
    state_cache = ProjectStateCache(cache_file, smart_cache=smart_cache)
    
    # Load state
    state = state_cache.load()
    
    # Bootstrap if cache is empty or has no epics
    if not state.epics:
        logger.info("Cache empty or no epics - running bootstrap...")
        state_cache.bootstrap(project_root)
        state_cache.save()
        state = state_cache.cache_data
    else:
        # Sync with file system (only re-parses changed stories)
        state_cache.sync(project_root)
        state = state_cache.cache_data
    
    # Reconstruct Project object linking Epics and Stories
    # ProjectState stores them disconnected after deserialization
    epics_map = state.epics
    
    # Clear stories in epics object to rebuild from fresh stories list
    for epic in epics_map.values():
        epic.stories = []
        
    # Re-populate epics with stories
    for story in state.stories.values():
        # Get epic ID from story_id (e.g., "5.4" -> "5")
        try:
            epic_num = story.story_id.split('.')[0]
            epic_key = f"epic-{epic_num}"
        except (AttributeError, IndexError):
            # Fallback to the epic field if story_id format is unexpected
            epic_key = f"epic-{story.epic}"
            
        # Handle case where epic key might differ or missing
        if epic_key in epics_map:
             epics_map[epic_key].stories.append(story)
        else:
             # Fallback: log warning or try alternative mapping
             logger.warning(f"Could not map story {story.story_id} to epic {epic_key}")
             pass

    # Sort stories in each epic by ID
    for epic in epics_map.values():
         epic.stories.sort(key=lambda s: sort_story_key(s.story_id))
    
    # Sort epics by ID
    sorted_epics = sorted(epics_map.values(), key=lambda e: sort_epic_key(e.epic_id))
    
    project = Project(
        name=state.project.get("name", "BMAD Dash"),
        phase=state.project.get("phase", "Implementation"),
        root_path=project_root,
        epics=sorted_epics,
        sprint_status_mtime=0.0 # Not used for invalidation anymore
    )
    
    # Build dashboard response
    response = build_dashboard_response(project)
    
    # Add cache_age_ms
    try:
        if os.path.exists(state_cache.cache_file):
            mtime = os.path.getmtime(state_cache.cache_file)
            age = (time.time() - mtime) * 1000
            response["cache_age_ms"] = age
        else:
            response["cache_age_ms"] = 0
    except OSError:
        response["cache_age_ms"] = 0
    
    # Add smart cache stats (Story 5.55)
    cache_stats = state_cache.get_cache_stats()
    if cache_stats:
        response["smart_cache"] = cache_stats
    
    return jsonify(response), 200

def sort_story_key(story_id):
    try:
        # Treat story_id as a semantic version: "5.55" sorts between "5.5" and "5.6"
        # Split into major.minor.patch
        parts = story_id.split('.')

        if len(parts) == 2:
            # Standard format: "5.6" or "5.55"
            major = int(parts[0])
            minor_str = parts[1]

            # Pad to ensure correct sorting: "5" becomes "50", "55" stays "55", "6" becomes "60"
            # This makes: 5.5 (50) < 5.55 (55) < 5.6 (60)
            if len(minor_str) == 1:
                minor = int(minor_str) * 10  # "6" → 60
            else:
                minor = int(minor_str)  # "55" → 55

            return (major, minor, 0)
        else:
            return (0, 0, 0)
    except:
        return (0, 0, 0)

def sort_epic_key(epic_id):
    try:
        return int(epic_id.replace("epic-", ""))
    except:
        return 0



def _get_current_story_focus(all_stories):
    """
    Shared helper to determine the "current focus" story
    
    Priority order:
    1. in-progress (actively being worked on)
    2. review (completed work awaiting review)
    3. ready-for-dev (next up for development)
    4. None (if no active stories, let caller decide what to show)
    
    Args:
        all_stories: List of Story objects
        
    Returns:
        Story object or None
    """
    # Priority 1: in-progress
    for story in all_stories:
        if story.status == "in-progress":
            return story
    
    # Priority 2: review
    for story in all_stories:
        if story.status == "review":
            return story
    
    # Priority 3: ready-for-dev
    for story in all_stories:
        if story.status == "ready-for-dev":
            return story
    
    # No active story found
    return None


def build_dashboard_response(project) -> Dict[str, Any]:
    """
    Build complete dashboard response from Project dataclass
    
    Args:
        project: Project dataclass from BMADParser
        
    Returns:
        Dictionary with project, breadcrumb, quick_glance, and kanban data
    """
    return {
        "project": build_project_data(project),
        "breadcrumb": build_breadcrumb(project),
        "quick_glance": build_quick_glance(project),
        "kanban": build_kanban(project),
        "action_card": build_action_card(project)
    }


def build_project_data(project) -> Dict[str, Any]:
    """
    Build project metadata section
    
    Args:
        project: Project dataclass
        
    Returns:
        Dictionary with name, phase, root_path, sprint_status_mtime
    """
    return {
        "name": project.name,
        "phase": project.phase,
        "root_path": project.root_path,
        "sprint_status_mtime": project.sprint_status_mtime
    }


def build_breadcrumb(project) -> Dict[str, Any]:
    """
    Build breadcrumb navigation hierarchy
    
    Logic:
    - Project: from project.name
    - Phase: from project.phase
    - Epic: find epic with status "in-progress" OR most recent epic with incomplete stories
    - Story: find story with status "in-progress" OR first "ready-for-dev" story
    - Task: find first task with status "todo" in current story
    
    Args:
        project: Project dataclass
        
    Returns:
        Dictionary with project, phase, epic, story, task hierarchy
    """
    breadcrumb = {
        "project": project.name,
        "phase": project.phase,
        "epic": None,
        "story": None,
        "task": None
    }
    
    current_epic = None
    
    # Strategy: Align Breadcrumb with Quick Glance (Current > Next > Fallback)
    
    # 1. Try to find "Current" story (in-progress / review)
    # This aligns with Quick Glance "Current Focus"
    target_story = None
    for epic in project.epics:
        for story in epic.stories:
            if story.status in ["in-progress", "review"]:
                target_story = story
                current_epic = epic
                break
        if target_story: 
            break
            
    # 2. If no current, find "Ready for Dev" (Next up)
    if not target_story:
        for epic in project.epics:
            for story in epic.stories:
                if story.status == "ready-for-dev":
                    target_story = story
                    current_epic = epic
                    break
            if target_story: 
                break

    # 3. If no ready, find first "Backlog" or "Todo" (Up Next)
    # This aligns with Quick Glance "Up Next"
    if not target_story:
        for epic in project.epics:
            for story in epic.stories:
                if story.status in ["todo", "backlog"] and not story.completed:
                    target_story = story
                    current_epic = epic
                    break
            if target_story: 
                break

    # 4. Fallback: Last completed epic (if everything is done)
    if not current_epic and project.epics:
        current_epic = project.epics[-1]
    
    if current_epic:
        breadcrumb["epic"] = {
            "id": current_epic.epic_id,
            "title": current_epic.title
        }
        
        if target_story and target_story.epic == int(current_epic.epic_id):
            breadcrumb["story"] = {
                "id": target_story.story_id,
                "title": target_story.title
            }
            
            # Find first todo task
            for task in target_story.tasks:
                if task.status == "todo":
                    breadcrumb["task"] = {
                        "id": task.task_id,
                        "title": task.title
                    }
                    break
    
    return breadcrumb


def build_quick_glance(project) -> Dict[str, Any]:
    """
    Build quick glance section showing Done/Current/Next stories
    
    Logic:
    - Done: Last story with status "done" (by completion date)
    - Current: First story with status "in-progress" OR "ready-for-dev"
    - Next: First story with status "backlog" OR "todo" after current
    
    Args:
        project: Project dataclass
        
    Returns:
        Dictionary with done, current, next story summaries
    """
    quick_glance = {
        "done": None,
        "current": None,
        "next": None
    }
    
    # Flatten all stories from all epics
    all_stories = []
    for epic in project.epics:
        all_stories.extend(epic.stories)
    
    # Find done story (last completed)
    # Include done stories regardless of whether they have a completed date
    done_stories = [s for s in all_stories if s.status == "done"]
    if done_stories:
        # Sort by completion date (most recent first), then by story_id (highest first) as tiebreaker
        def sort_key(story):
            # Parse story_id with semantic versioning (5.5 < 5.55 < 5.6)
            # Single-digit minors pad to tens place: "5" -> 50, "6" -> 60, "7" -> 70
            # Two-digit minors stay as-is: "55" -> 55
            try:
                parts = story.story_id.split('.')
                epic_num = int(parts[0]) if len(parts) > 0 else 0
                if len(parts) > 1:
                    minor_str = parts[1]
                    if len(minor_str) == 1:
                        story_num = int(minor_str) * 10  # "5" -> 50, "6" -> 60, "7" -> 70
                    else:
                        story_num = int(minor_str)  # "55" -> 55
                else:
                    story_num = 0
                story_tuple = (epic_num, story_num)
            except (ValueError, AttributeError):
                story_tuple = (0, 0)
            
            # Key priority:
            # 1. Completion Date (if exists), else last_updated (if exists), else "0000-00-00"
            # 2. Epic Number
            # 3. Story Number
            # Use last_updated as fallback for missing completed dates
            if story.completed:
                date_val = story.completed
            elif hasattr(story, 'last_updated') and story.last_updated:
                date_val = story.last_updated
            else:
                date_val = "0000-00-00"
            
            return (date_val, story_tuple)
        
        done_stories.sort(key=sort_key, reverse=True)
        done_story = done_stories[0]
        quick_glance["done"] = {
            "story_id": done_story.story_id,
            "title": done_story.title,
            "completed": done_story.completed
        }
    
    # Find current story (in-progress, review, or ready-for-dev)
    current_story = _get_current_story_focus(all_stories)
    
    if current_story:
        # Calculate progress
        total_tasks = len(current_story.tasks)
        official_done = len([t for t in current_story.tasks if t.status == "done" and not getattr(t, 'inferred', False)])
        inferred_done = len([t for t in current_story.tasks if getattr(t, 'inferred', False)])
        done_tasks = official_done + inferred_done
        
        # Find current task (first in-progress, or first todo)
        current_task_title = "No active task"
        for task in current_story.tasks:
            if task.status == "in-progress":
                current_task_title = task.title
                break
        
        if current_task_title == "No active task":
            for task in current_story.tasks:
                if task.status == "todo":
                    current_task_title = task.title
                    break

        progress_str = f"{done_tasks}/{total_tasks} tasks"
        if inferred_done > 0:
            progress_str = f"{done_tasks}/{total_tasks} ({inferred_done} inferred)"

        quick_glance["current"] = {
            "story_id": current_story.story_id,
            "title": current_story.title,
            "status": current_story.status,
            "progress": progress_str,
            "current_task": current_task_title
        }
        
        # Find next story (after current)
        current_index = all_stories.index(current_story)
        for i in range(current_index + 1, len(all_stories)):
            next_story = all_stories[i]
            if next_story.status in ["backlog", "todo", "ready-for-dev"]:
                quick_glance["next"] = {
                    "story_id": next_story.story_id,
                    "title": next_story.title,
                    "status": next_story.status
                }
                break
    else:
        # No current story - find first backlog/todo story for "next"
        for story in all_stories:
            if story.status in ["backlog", "todo"]:
                quick_glance["next"] = {
                    "story_id": story.story_id,
                    "title": story.title,
                    "status": story.status
                }
                break
    
    return quick_glance


def build_kanban(project) -> Dict[str, List[Dict[str, Any]]]:
    """
    Build kanban board grouping stories by status
    
    Status Mapping:
    - todo: ["backlog", "todo"]
    - in_progress: ["ready-for-dev", "in-progress"]
    - review: ["review"]
    - done: ["done", "complete"]
    
    Args:
        project: Project dataclass
        
    Returns:
        Dictionary with todo, in_progress, review, done story lists
    """
    STATUS_GROUPS = {
        "todo": ["backlog", "todo"],
        "in_progress": ["ready-for-dev", "in-progress"],
        "review": ["review"],
        "done": ["done", "complete"]
    }
    
    kanban = {
        "todo": [],
        "in_progress": [],
        "review": [],
        "done": []
    }
    
    # Flatten all stories and group by status
    for epic in project.epics:
        for story in epic.stories:
            story_data = {
                "story_id": story.story_id, # Use story_id
                "id": story.story_id,       # Alias for frontend compatibility
                "title": story.title,
                "epic": story.epic,
                "status": story.status,
                "last_updated": story.last_updated if hasattr(story, 'last_updated') else None,
                "tasks": [task.to_dict() for task in story.tasks],
                "evidence": story.evidence if hasattr(story, 'evidence') else {}
            }
            
            # Add completed date for done stories
            if story.status in STATUS_GROUPS["done"] and story.completed:
                story_data["completed"] = story.completed
            
            # Add to appropriate column
            for group_name, statuses in STATUS_GROUPS.items():
                if story.status in statuses:
                    kanban[group_name].append(story_data)
                    break
    
    return kanban


def build_action_card(project) -> Dict[str, Any]:
    """
    Build action card with three layers: Story > Task > Command
    
    Logic:
    - Layer 1 (Story): Current story title and acceptance criteria summary
    - Layer 2 (Task): Current task description with progress (e.g., "Task 2/5: Write API route handler")
    - Layer 3 (Command): Context-specific BMAD workflow command based on story state
    
    Command Suggestions:
    - todo/ready-for-dev: /bmad-bmm-workflows-dev-story
    - in-progress: /bmad-bmm-workflows-dev-story (continuing)
    - review: /bmad-bmm-workflows-code-review
    - done: /bmad-bmm-workflows-create-story [next_story_id]
    
    Args:
        project: Project dataclass
        
    Returns:
        Dictionary with story_layer, task_layer, command_layer
    """
    action_card = {
        "story_layer": None,
        "task_layer": None,
        "command_layer": None
    }
    
    # Flatten all stories from all epics
    all_stories = []
    for epic in project.epics:
        all_stories.extend(epic.stories)
    
    # Find current story using shared helper
    current_story = _get_current_story_focus(all_stories)
    
    # If no active story, check if all stories are done (trigger retrospective)
    if not current_story:
        done_stories = [s for s in all_stories if s.status == "done"]
        if done_stories and len(done_stories) == len(all_stories):
            # All stories complete - suggest retrospective
            action_card["command_layer"] = {
                "command": "/bmad:bmm:workflows:retrospective",
                "description": "All stories complete - run retrospective"
            }
            # Use most recent completed story for context
            done_stories.sort(key=lambda s: s.completed if s.completed else "0000-00-00", reverse=True)
            most_recent = done_stories[0]
            action_card["story_layer"] = {
                "story_id": most_recent.story_id,
                "title": most_recent.title,
                "status": most_recent.status,
                "acceptance_criteria_summary": []
            }
            action_card["task_layer"] = {
                "task_id": None,
                "title": "Epic complete",
                "status": "done",
                "progress": f"{len(done_stories)}/{len(all_stories)} stories"
            }
            return action_card
        
        # Not all done, find first todo/backlog for "next" suggestion
        for story in all_stories:
            if story.status in ["todo", "backlog"]:
                # Show as "next" not "current" by setting command to create-story
                action_card["command_layer"] = {
                    "command": f"/bmad:bmm:workflows:create-story {story.story_id}",
                    "description": f"Start next story: {story.title}"
                }
                action_card["story_layer"] = {
                    "story_id": story.story_id,
                    "title": story.title,
                    "status": story.status,
                    "acceptance_criteria_summary": []
                }
                action_card["task_layer"] = {
                    "task_id": None,
                    "title": "Story not started",
                    "status": "none",
                    "progress": "0/0 tasks"
                }
                return action_card
        
        # Truly no stories - suggest creating first story
        action_card["command_layer"] = {
            "command": "/bmad:bmm:workflows:create-story",
            "description": "No active stories - create first story"
        }
        return action_card
    
    if current_story:
        # Layer 1: Story information
        # Extract acceptance criteria summary (first 3 criteria or all if fewer)
        ac_summary = []
        if hasattr(current_story, 'acceptance_criteria') and current_story.acceptance_criteria:
            ac_summary = current_story.acceptance_criteria[:3]
        
        action_card["story_layer"] = {
            "story_id": current_story.story_id,
            "title": current_story.title,
            "status": current_story.status,
            "acceptance_criteria_summary": ac_summary
        }
        
        # Layer 2: Task information
        total_tasks = len(current_story.tasks)
        done_tasks = len([t for t in current_story.tasks if t.status == "done"])
        
        # Find current task (first in-progress, or first todo)
        current_task = None
        current_task_index = 0
        
        for i, task in enumerate(current_story.tasks):
            if task.status == "in-progress":
                current_task = task
                current_task_index = i + 1  # 1-indexed
                break
        
        if not current_task:
            for i, task in enumerate(current_story.tasks):
                if task.status == "todo":
                    current_task = task
                    current_task_index = i + 1  # 1-indexed
                    break
        
        if current_task:
            action_card["task_layer"] = {
                "task_id": current_task.task_id,
                "title": current_task.title,
                "status": current_task.status,
                "progress": f"Task {current_task_index}/{total_tasks}"
            }
        else:
            # No active task
            action_card["task_layer"] = {
                "task_id": None,
                "title": "No active task",
                "status": "none",
                "progress": f"0/{total_tasks} tasks"
            }
        
        # Layer 3: Command suggestion based on story status
        command = ""
        command_description = ""
        
        if current_story.status in ["todo", "ready-for-dev"]:
            command = f"/bmad:bmm:workflows:dev-story {current_story.story_id}"
            command_description = "Start or continue development on this story"
        elif current_story.status == "in-progress":
            command = f"/bmad:bmm:workflows:dev-story {current_story.story_id}"
            command_description = "Continue development on this story"
        elif current_story.status == "review":
            command = f"/bmad:bmm:workflows:code-review {current_story.story_id}"
            command_description = "Run adversarial code review"
        
        action_card["command_layer"] = {
            "command": command,
            "description": command_description
        }
    else:
        # No stories found - suggest creating first story
        action_card["command_layer"] = {
            "command": "/bmad:bmm:workflows:create-story",
            "description": "No active stories - create first story"
        }
    
    return action_card


@dashboard_bp.route('/api/cache/stats', methods=['GET'])
@handle_api_errors
def get_cache_stats():
    """
    Get SmartCache statistics for the project.
    
    Query params:
        project_root: Path to the project root directory
        
    Returns:
        JSON with cache statistics including total stories, status counts, cache age
    """
    project_root = request.args.get('project_root')
    
    if not project_root:
        raise ValueError("project_root parameter is required")
    
    if not os.path.exists(project_root):
        raise FileNotFoundError(f"Project not found: {project_root}")
    
    smart_cache = SmartCache(project_root)
    stats = smart_cache.get_cache_stats()
    
    return jsonify(stats), 200


@dashboard_bp.route('/api/dashboard/story/<story_id>', methods=['GET'])
@handle_api_errors
def get_story_details(story_id):
    """
    Returns full story details (markdown + tasks) for the detail modal.
    """
    project_root = request.args.get('project_root')
    if not project_root:
        raise ValueError("project_root parameter is required")

    smart_cache = SmartCache(project_root)
    cache_file = os.path.join(project_root, "_bmad-output/implementation-artifacts/project-state.json")
    state_cache = ProjectStateCache(cache_file, smart_cache=smart_cache)
    
    state = state_cache.load()
    story = state.stories.get(story_id)
    
    if not story:
        raise FileNotFoundError(f"Story {story_id} not found in cache")
    
    # Load markdown content if file exists
    content = ""
    if story.file_path and os.path.exists(story.file_path):
        try:
            with open(story.file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            logger.error(f"Error reading story file {story.file_path}: {e}")
            content = f"Error reading story file: {str(e)}"

    return jsonify({
        "story_id": story.story_id,
        "title": story.title,
        "status": story.status,
        "tasks": [task.to_dict() for task in story.tasks],
        "content": content,
        "evidence": story.evidence
    })


@dashboard_bp.route('/api/cache/clear', methods=['POST'])
@handle_api_errors
def clear_cache():
    """
    Clear all SmartCache data for the project.
    
    Query params:
        project_root: Path to the project root directory
        
    Returns:
        JSON confirmation with success message
    """
    project_root = request.args.get('project_root')
    
    if not project_root:
        raise ValueError("project_root parameter is required")
    
    if not os.path.exists(project_root):
        raise FileNotFoundError(f"Project not found: {project_root}")
    
    smart_cache = SmartCache(project_root)
    smart_cache.clear_project_cache()
    
    # Also clear the project state cache to force a full re-bootstrap (Story 5.55 Fix)
    state_cache_file = os.path.join(project_root, "_bmad-output/implementation-artifacts/project-state.json")
    if os.path.exists(state_cache_file):
        os.remove(state_cache_file)
        logger.info(f"Deleted project-state.json for full refresh: {state_cache_file}")
    
    logger.info(f"Cleared SmartCache for project: {project_root}")
    
    return jsonify({"success": True, "message": "Cache cleared successfully. Next load will perform full bootstrap."}), 200


@dashboard_bp.route('/api/cache/invalidate/<story_id>', methods=['POST'])
@handle_api_errors
def invalidate_story_cache(story_id: str):
    """
    Invalidate SmartCache for a specific story.
    Forces the story to be re-processed on next load.
    
    Query params:
        project_root: Path to the project root directory
        
    Path params:
        story_id: Story identifier to invalidate (e.g., "5.4")
        
    Returns:
        JSON confirmation with success message
    """
    project_root = request.args.get('project_root')
    
    if not project_root:
        raise ValueError("project_root parameter is required")
    
    if not os.path.exists(project_root):
        raise FileNotFoundError(f"Project not found: {project_root}")
    
    smart_cache = SmartCache(project_root)
    smart_cache.invalidate_story(story_id)
    
    logger.info(f"Invalidated SmartCache for story {story_id} in project: {project_root}")
    
    return jsonify({"success": True, "message": f"Cache invalidated for story {story_id}"}), 200

