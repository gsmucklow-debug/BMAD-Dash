"""
BMAD Dash - Dashboard API Endpoint
GET /api/dashboard - Returns project overview with epics and stories
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


@dashboard_bp.route('/api/dashboard', methods=['GET'])
@handle_api_errors
def get_dashboard():
    """
    Returns dashboard data including project overview, breadcrumb, quick_glance, and kanban
    
    Query Parameters:
        project_root (required): Absolute path to project root directory
        
    Returns:
        200: Dashboard data with project, breadcrumb, quick_glance, kanban
        400: Missing or invalid project_root parameter
        404: Project path not found
        500: Parsing or internal error
    """
    # Extract and validate project_root parameter
    project_root = request.args.get('project_root')
    
    if not project_root:
        raise ValueError("project_root parameter is required")
    
    if not os.path.exists(project_root):
        raise FileNotFoundError(f"Project not found: {project_root}")
    
    # Determine sprint-status.yaml path for cache invalidation
    sprint_status_path = os.path.join(
        project_root,
        "_bmad-output/implementation-artifacts/sprint-status.yaml"
    )
    
    # Try to get cached response
    cache_key = f"dashboard_{project_root}"
    cached_response = _cache.get(cache_key, sprint_status_path)
    
    if cached_response:
        logger.info(f"Cache HIT for {cache_key}")
        return jsonify(cached_response), 200
    
    logger.info(f"Cache MISS for {cache_key} - parsing project")
    
    # Parse project using BMADParser
    parser = BMADParser(project_root)
    project = parser.parse_project()
    
    if not project:
        raise Exception(f"Failed to parse project at {project_root}")
    
    # Build dashboard response
    response = build_dashboard_response(project)
    
    # Cache the response
    _cache.set(cache_key, response, sprint_status_path)
    
    return jsonify(response), 200


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
        "kanban": build_kanban(project)
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
        
        # Find current story (in-progress or ready-for-dev)
        current_story = None
        for story in current_epic.stories:
            if story.status == "in-progress":
                current_story = story
                break
        
        if not current_story:
            for story in current_epic.stories:
                if story.status == "ready-for-dev":
                    current_story = story
                    break
        
        if current_story:
            breadcrumb["story"] = {
                "id": current_story.story_id,
                "title": current_story.title
            }
            
            # Find first todo task
            for task in current_story.tasks:
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
    done_stories = [s for s in all_stories if s.status == "done" and s.completed]
    if done_stories:
        # Sort by completion date (most recent first), then by story_id (highest first) as tiebreaker
        def sort_key(story):
            # Parse story_id (e.g., "3.1" -> (3, 1)) for proper numeric comparison
            try:
                parts = story.story_id.split('.')
                epic_num = int(parts[0]) if len(parts) > 0 else 0
                story_num = int(parts[1]) if len(parts) > 1 else 0
                story_tuple = (epic_num, story_num)
            except (ValueError, AttributeError):
                story_tuple = (0, 0)
            
            # Key priority:
            # 1. Completion Date (if exists)
            # 2. Epic Number
            # 3. Story Number
            # Use '0000-00-00' for missing dates so they sort last if reverse=True, 
            # BUT we actually want "done" stories without dates to potentially be recent if date was just missed.
            # A safer bet is: if date is missing, rely on story_id (assuming higher IDs are newer).
            date_val = story.completed if story.completed else "0000-00-00"
            
            return (date_val, story_tuple)
        
        done_stories.sort(key=sort_key, reverse=True)
        done_story = done_stories[0]
        quick_glance["done"] = {
            "story_id": done_story.story_id,
            "title": done_story.title,
            "completed": done_story.completed
        }
    
    # Find current story (in-progress, review, or ready-for-dev)
    # Priority order: in-progress > review > ready-for-dev
    current_story = None
    for story in all_stories:
        if story.status == "in-progress":
            current_story = story
            break
    
    if not current_story:
        for story in all_stories:
            if story.status == "review":
                current_story = story
                break
    
    if not current_story:
        for story in all_stories:
            if story.status == "ready-for-dev":
                current_story = story
                break
    
    if current_story:
        # Calculate progress
        total_tasks = len(current_story.tasks)
        done_tasks = len([t for t in current_story.tasks if t.status == "done"])
        
        quick_glance["current"] = {
            "story_id": current_story.story_id,
            "title": current_story.title,
            "status": current_story.status,
            "progress": f"{done_tasks}/{total_tasks} tasks"
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
                "tasks": [task.to_dict() for task in story.tasks]
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
