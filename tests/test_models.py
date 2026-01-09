"""
BMAD Dash - Data Model Tests
Tests for all data models and serialization
"""
import pytest
from datetime import datetime
from backend.models.project import Project
from backend.models.epic import Epic
from backend.models.story import Story
from backend.models.task import Task
from backend.models.git_evidence import GitCommit, GitEvidence
from backend.models.test_evidence import TestEvidence


class TestProjectModel:
    """Test Project dataclass"""
    
    def test_project_creation(self):
        """Test creating a Project instance"""
        project = Project(
            name="Test Project",
            phase="Implementation",
            root_path="/path/to/project"
        )
        
        assert project.name == "Test Project"
        assert project.phase == "Implementation"
        assert project.root_path == "/path/to/project"
        assert project.epics == []
        assert project.sprint_status_mtime == 0.0
    
    def test_project_to_dict(self):
        """Test Project serialization"""
        epic = Epic(epic_id="1", title="Test Epic", status="backlog")
        project = Project(
            name="Test Project",
            phase="Planning",
            root_path="/test",
            epics=[epic],
            sprint_status_mtime=123.456
        )
        
        data = project.to_dict()
        
        assert data['name'] == "Test Project"
        assert data['phase'] == "Planning"
        assert data['root_path'] == "/test"
        assert len(data['epics']) == 1
        assert data['sprint_status_mtime'] == 123.456
    
    def test_project_from_dict(self):
        """Test Project deserialization"""
        data = {
            "name": "Test Project",
            "phase": "Solutioning",
            "root_path": "/test",
            "epics": [
                {"epic_id": "1", "title": "Epic 1", "status": "done", "stories": [], "progress": {"total": 0, "done": 0}}
            ],
            "sprint_status_mtime": 789.012
        }
        
        project = Project.from_dict(data)
        
        assert project.name == "Test Project"
        assert project.phase == "Solutioning"
        assert len(project.epics) == 1
        assert project.epics[0].title == "Epic 1"


class TestEpicModel:
    """Test Epic dataclass"""
    
    def test_epic_creation(self):
        """Test creating an Epic instance"""
        epic = Epic(
            epic_id="epic-1",
            title="Core Features",
            status="in-progress"
        )
        
        assert epic.epic_id == "epic-1"
        assert epic.title == "Core Features"
        assert epic.status == "in-progress"
        assert epic.stories == []
        assert epic.progress == {"total": 0, "done": 0}
    
    def test_epic_to_dict(self):
        """Test Epic serialization"""
        story = Story(
            story_id="1.1",
            story_key="1-1-test",
            title="Test Story",
            status="done",
            epic=1
        )
        epic = Epic(
            epic_id="1",
            title="Test Epic",
            status="done",
            stories=[story],
            progress={"total": 1, "done": 1}
        )
        
        data = epic.to_dict()
        
        assert data['epic_id'] == "1"
        assert data['title'] == "Test Epic"
        assert len(data['stories']) == 1
        assert data['progress']['total'] == 1
        assert data['progress']['done'] == 1


class TestStoryModel:
    """Test Story dataclass"""
    
    def test_story_creation(self):
        """Test creating a Story instance"""
        story = Story(
            story_id="1.1",
            story_key="1-1-test-story",
            title="Test Story",
            status="in-progress",
            epic=1
        )
        
        assert story.story_id == "1.1"
        assert story.story_key == "1-1-test-story"
        assert story.title == "Test Story"
        assert story.status == "in-progress"
        assert story.epic == 1
        assert story.tasks == []
    
    def test_story_to_dict(self):
        """Test Story serialization"""
        task = Task(task_id="1", title="Do thing", status="done")
        story = Story(
            story_id="2.3",
            story_key="2-3-another-story",
            title="Another Story",
            status="done",
            epic=2,
            tasks=[task],
            created="2026-01-09",
            completed="2026-01-10",
            file_path="/path/to/story.md",
            mtime=999.888
        )
        
        data = story.to_dict()
        
        assert data['story_id'] == "2.3"
        assert data['title'] == "Another Story"
        assert len(data['tasks']) == 1
        assert data['created'] == "2026-01-09"
        assert data['completed'] == "2026-01-10"
        assert data['mtime'] == 999.888


class TestTaskModel:
    """Test Task dataclass"""
    
    def test_task_creation(self):
        """Test creating a Task instance"""
        task = Task(
            task_id="task-1",
            title="Implement feature",
            status="todo"
        )
        
        assert task.task_id == "task-1"
        assert task.title == "Implement feature"
        assert task.status == "todo"
        assert task.subtasks == []
    
    def test_task_with_subtasks(self):
        """Test Task with subtasks"""
        task = Task(
            task_id="task-2",
            title="Complex task",
            status="done",
            subtasks=[
                {"text": "Subtask 1", "status": "done"},
                {"text": "Subtask 2", "status": "done"}
            ]
        )
        
        assert len(task.subtasks) == 2
        assert task.subtasks[0]['text'] == "Subtask 1"
        assert task.subtasks[0]['status'] == "done"
    
    def test_task_to_dict(self):
        """Test Task serialization"""
        task = Task(
            task_id="task-3",
            title="Test task",
            status="todo",
            subtasks=[{"text": "Sub", "status": "todo"}]
        )
        
        data = task.to_dict()
        
        assert data['task_id'] == "task-3"
        assert data['title'] == "Test task"
        assert len(data['subtasks']) == 1


class TestGitEvidenceModels:
    """Test Git evidence models"""
    
    def test_git_commit_creation(self):
        """Test creating a GitCommit"""
        commit = GitCommit(
            sha="abc123",
            message="Initial commit",
            author="Test User",
            timestamp=datetime.now(),
            files_changed=["file1.py", "file2.py"]
        )
        
        assert commit.sha == "abc123"
        assert commit.message == "Initial commit"
        assert len(commit.files_changed) == 2
    
    def test_git_commit_serialization(self):
        """Test GitCommit to_dict"""
        now = datetime.now()
        commit = GitCommit(
            sha="def456",
            message="Fix bug",
            author="Dev",
            timestamp=now
        )
        
        data = commit.to_dict()
        
        assert data['sha'] == "def456"
        assert data['message'] == "Fix bug"
        assert 'timestamp' in data
    
    def test_git_evidence_creation(self):
        """Test creating GitEvidence"""
        commit = GitCommit(
            sha="xyz789",
            message="Feature",
            author="Me",
            timestamp=datetime.now()
        )
        evidence = GitEvidence(
            story_id="1.1",
            commits=[commit]
        )
        
        assert evidence.story_id == "1.1"
        assert len(evidence.commits) == 1
        assert evidence.commits[0].sha == "xyz789"


class TestTestEvidenceModel:
    """Test TestEvidence model"""
    
    def test_test_evidence_creation(self):
        """Test creating TestEvidence"""
        evidence = TestEvidence(
            story_id="2.1",
            test_files=["test_one.py", "test_two.py"],
            pass_count=10,
            fail_count=2
        )
        
        assert evidence.story_id == "2.1"
        assert len(evidence.test_files) == 2
        assert evidence.pass_count == 10
        assert evidence.fail_count == 2
    
    def test_test_evidence_serialization(self):
        """Test TestEvidence to_dict"""
        evidence = TestEvidence(
            story_id="3.2",
            test_files=["test.py"],
            pass_count=5,
            fail_count=0
        )
        
        data = evidence.to_dict()
        
        assert data['story_id'] == "3.2"
        assert len(data['test_files']) == 1
        assert data['pass_count'] == 5
        assert data['fail_count'] == 0


class TestNestedSerialization:
    """Test serialization of nested structures"""
    
    def test_full_project_serialization(self):
        """Test serializing complete project with all nested models"""
        task = Task(task_id="t1", title="Task", status="done")
        story = Story(
            story_id="1.1",
            story_key="1-1-test",
            title="Story",
            status="done",
            epic=1,
            tasks=[task]
        )
        epic = Epic(
            epic_id="1",
            title="Epic",
            status="done",
            stories=[story],
            progress={"total": 1, "done": 1}
        )
        project = Project(
            name="Project",
            phase="Implementation",
            root_path="/test",
            epics=[epic]
        )
        
        # Serialize to dict
        data = project.to_dict()
        
        # Verify nested structure
        assert data['name'] == "Project"
        assert len(data['epics']) == 1
        assert len(data['epics'][0]['stories']) == 1
        assert len(data['epics'][0]['stories'][0]['tasks']) == 1
        assert data['epics'][0]['stories'][0]['tasks'][0]['title'] == "Task"
    
    def test_full_project_deserialization(self):
        """Test deserializing complete nested project"""
        data = {
            "name": "Project",
            "phase": "Implementation",
            "root_path": "/test",
            "epics": [
                {
                    "epic_id": "1",
                    "title": "Epic 1",
                    "status": "done",
                    "stories": [
                        {
                            "story_id": "1.1",
                            "story_key": "1-1-test",
                            "title": "Story 1",
                            "status": "done",
                            "epic": 1,
                            "tasks": [
                                {"task_id": "t1", "title": "Task 1", "status": "done", "subtasks": []}
                            ],
                            "created": "",
                            "completed": None,
                            "file_path": "",
                            "mtime": 0.0
                        }
                    ],
                    "progress": {"total": 1, "done": 1}
                }
            ],
            "sprint_status_mtime": 0.0
        }
        
        project = Project.from_dict(data)
        
        assert project.name == "Project"
        assert len(project.epics) == 1
        assert project.epics[0].title == "Epic 1"
        assert len(project.epics[0].stories) == 1
        assert project.epics[0].stories[0].title == "Story 1"
        assert len(project.epics[0].stories[0].tasks) == 1
        assert project.epics[0].stories[0].tasks[0].title == "Task 1"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
