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
    
    # Find current epic (in-progress or first with incomplete stories)
    current_epic = None
    for epic in project.epics:
        if epic.status == "in-progress":
            current_epic = epic
            break
    
    if not current_epic:
        # Find first epic with incomplete stories
        for epic in project.epics:
            incomplete_stories = [s for s in epic.stories if s.status != "done"]
            if incomplete_stories:
                current_epic = epic
                break
    
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
        # Sort by completion date (most recent first)
        done_stories.sort(key=lambda s: s.completed, reverse=True)
        done_story = done_stories[0]
        quick_glance["done"] = {
            "story_id": done_story.story_id,
            "title": done_story.title,
            "completed": done_story.completed
        }
    
    # Find current story (in-progress or ready-for-dev)
    current_story = None
    for story in all_stories:
        if story.status == "in-progress":
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
                    "title": next_story.title
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
                "story_id": story.story_id,
                "title": story.title,
                "epic": story.epic,
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
