
import pytest
from backend.models.story import Story
from backend.models.task import Task as TaskModel

def test_story_evidence_field():
    story = Story(story_id="1", story_key="key", title="title", status="todo", epic=1)
    # This should fail if field doesn't exist (type checker) or just work if dynamic
    # But specifically I want to use it in init
    story = Story(
        story_id="1", story_key="key", title="title", status="todo", epic=1,
        evidence={"commits": 5}
    )
    assert story.evidence["commits"] == 5

def test_story_tasks_structure():
    story = Story(story_id="1", story_key="key", title="title", status="todo", epic=1)
    task1 = TaskModel(task_id="1", title="t1", status="done")
    task2 = TaskModel(task_id="2", title="t2", status="todo")
    story.tasks = [task1, task2]
    
    data = story.to_dict()
    assert "tasks" in data
    # Check if it matches new schema
    # Schema: tasks: { done: 1, total: 2, items: [...] }
    assert isinstance(data["tasks"], dict)
    assert data["tasks"]["done"] == 1
    assert data["tasks"]["total"] == 2
    assert len(data["tasks"]["items"]) == 2
