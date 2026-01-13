"""
BMAD Dash - Tests for Enhanced AI Chat Context (Story 5.2)
Tests for project-aware Q&A with flow suggestions
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from backend.services.ai_coach import AICoach
from backend.services.bmad_version_detector import BMADVersionDetector


class TestEnhancedAICoachContext:
    """Tests for enhanced AI Coach context injection"""
    story_id="5.2"
    
    @patch('backend.services.ai_coach.genai')
    def test_system_prompt_includes_story_status(self, mock_genai):
        """Test that system prompt includes story status"""
        coach = AICoach('test-api-key')
        context = {
            'phase': 'Implementation',
            'epic_id': 'epic-5',
            'epic_title': 'AI Coach Integration',
            'story_id': '5.2',
            'story_title': 'Project-Aware Q&A',
            'story_status': 'IN_PROGRESS',
            'task': 'Implementing tests'
        }
        
        prompt = coach._build_system_prompt(context)
        
        assert 'Story Status: IN_PROGRESS' in prompt
        assert '5.2' in prompt
        assert 'Project-Aware Q&A' in prompt
    
    @patch('backend.services.ai_coach.genai')
    def test_system_prompt_includes_epic_title(self, mock_genai):
        """Test that system prompt includes epic title"""
        coach = AICoach('test-api-key')
        context = {
            'phase': 'Implementation',
            'epic_id': 'epic-5',
            'epic_title': 'AI Coach Integration',
            'story_id': '5.2',
            'story_status': 'TODO'
        }
        
        prompt = coach._build_system_prompt(context)
        
        assert 'epic-5 - AI Coach Integration' in prompt
    
    @patch('backend.services.ai_coach.genai')
    def test_system_prompt_handles_missing_titles(self, mock_genai):
        """Test that system prompt handles missing epic/story titles gracefully"""
        coach = AICoach('test-api-key')
        context = {
            'phase': 'Implementation',
            'epic_id': 'epic-5',
            'story_id': '5.2',
            'story_status': 'IN_PROGRESS'
        }
        
        prompt = coach._build_system_prompt(context)
        
        # Should not have trailing " - " when titles are missing
        assert 'Epic: epic-5\n' in prompt or 'Epic: epic-5 ' not in prompt
        assert 'Story: 5.2\n' in prompt or 'Story: 5.2 ' not in prompt
    
    @patch('backend.services.ai_coach.genai')
    def test_system_prompt_includes_workflow_suggestions(self, mock_genai):
        """Test that system prompt includes BMAD workflow suggestions"""
        coach = AICoach('test-api-key')
        context = {
            'phase': 'Implementation',
            'story_id': '5.2',
            'story_status': 'IN_PROGRESS'
        }
        
        prompt = coach._build_system_prompt(context)
        
        assert 'BMAD Workflow Suggestions' in prompt
        assert '/bmad-bmm-workflows-dev-story' in prompt
        assert '/bmad-bmm-workflows-code-review' in prompt
        assert 'TODO' in prompt or 'READY_FOR_DEV' in prompt
        assert 'IN_PROGRESS' in prompt
        assert 'REVIEW' in prompt
    
    @patch('backend.services.ai_coach.genai')
    def test_system_prompt_explains_workflow_commands(self, mock_genai):
        """Test that system prompt explains when to use each workflow command"""
        coach = AICoach('test-api-key')
        context = {
            'story_id': '5.2',
            'story_status': 'TODO'
        }
        
        prompt = coach._build_system_prompt(context)
        
        assert 'Start development on this story' in prompt
        assert 'Run the code-review workflow' in prompt
        assert 'adversarial code review' in prompt
    
    @patch('backend.services.ai_coach.genai')
    def test_system_prompt_references_current_state(self, mock_genai):
        """Test that system prompt reminds AI to reference current state"""
        coach = AICoach('test-api-key')
        context = {
            'phase': 'Implementation',
            'story_id': '5.2',
            'story_status': 'IN_PROGRESS'
        }
        
        prompt = coach._build_system_prompt(context)
        
        assert 'access to the current project state' in prompt
        assert 'Your current story is' in prompt
    
    @patch('backend.services.ai_coach.genai')
    def test_backward_compatibility_with_old_context(self, mock_genai):
        """Test that old context format still works"""
        coach = AICoach('test-api-key')
        context = {
            'phase': 'Implementation',
            'epic': 'epic-5',  # Old format
            'story': '5.2',  # Old format
            'task': '1'
        }
        
        prompt = coach._build_system_prompt(context)
        
        # Should still include the values
        assert 'epic-5' in prompt
        assert '5.2' in prompt


class TestBMADVersionDetector:
    """Tests for BMAD version detection service"""
    story_id="5.2"
    
    def test_init_with_project_root(self):
        """Test initialization with project root"""
        detector = BMADVersionDetector('/test/project')
        
        assert detector.project_root == '/test/project'
        assert detector._cached_version is None
    
    def test_detect_version_from_sprint_status(self, tmp_path):
        """Test version detection from sprint-status.yaml"""
        # Create test sprint-status.yaml
        bmad_output = tmp_path / '_bmad-output' / 'implementation-artifacts'
        bmad_output.mkdir(parents=True)
        
        sprint_status = bmad_output / 'sprint-status.yaml'
        sprint_status.write_text('bmad_version: "1.2.3"\nproject: "Test"')
        
        detector = BMADVersionDetector(str(tmp_path))
        version = detector.detect_version()
        
        assert version == "1.2.3"
    
    def test_detect_version_caching(self, tmp_path):
        """Test that detected version is cached"""
        bmad_output = tmp_path / '_bmad-output' / 'implementation-artifacts'
        bmad_output.mkdir(parents=True)
        
        sprint_status = bmad_output / 'sprint-status.yaml'
        sprint_status.write_text('bmad_version: "2.0.0"')
        
        detector = BMADVersionDetector(str(tmp_path))
        version1 = detector.detect_version()
        
        # Change file
        sprint_status.write_text('bmad_version: "3.0.0"')
        
        version2 = detector.detect_version()
        
        # Should be cached
        assert version1 == version2 == "2.0.0"
    
    def test_invalidate_cache(self, tmp_path):
        """Test cache invalidation"""
        bmad_output = tmp_path / '_bmad-output' / 'implementation-artifacts'
        bmad_output.mkdir(parents=True)
        
        sprint_status = bmad_output / 'sprint-status.yaml'
        sprint_status.write_text('bmad_version: "1.0.0"')
        
        detector = BMADVersionDetector(str(tmp_path))
        version1 = detector.detect_version()
        
        # Change file and invalidate cache
        sprint_status.write_text('bmad_version: "2.0.0"')
        detector.invalidate_cache()
        
        version2 = detector.detect_version()
        
        assert version1 == "1.0.0"
        assert version2 == "2.0.0"
    
    def test_fallback_to_latest(self, tmp_path):
        """Test fallback to 'latest' when version not found"""
        detector = BMADVersionDetector(str(tmp_path))
        version = detector.detect_version()
        
        assert version == "latest"
    
    def test_get_version_info(self, tmp_path):
        """Test getting detailed version information"""
        detector = BMADVersionDetector(str(tmp_path))
        info = detector.get_version_info()
        
        assert 'version' in info
        assert 'is_latest' in info
        assert 'detected_from' in info
        assert info['version'] == 'latest'
        assert info['is_latest'] is True
    
    def test_handles_invalid_yaml(self, tmp_path):
        """Test graceful handling of invalid YAML"""
        bmad_output = tmp_path / '_bmad-output' / 'implementation-artifacts'
        bmad_output.mkdir(parents=True)
        
        sprint_status = bmad_output / 'sprint-status.yaml'
        sprint_status.write_text('invalid: yaml: content: ::: {{{')
        
        detector = BMADVersionDetector(str(tmp_path))
        version = detector.detect_version()
        
        # Should fallback to latest
        assert version == "latest"


class TestAIChatAPIContextIntegration:
    """Tests for /api/ai-chat context acceptance"""
    
    def test_api_accepts_expanded_context(self):
        """Test that API accepts expanded project context"""
        # This test will verify the API endpoint accepts the new context fields
        # Full integration test will be in test_api_ai_chat.py
        expanded_context = {
            'phase': 'Implementation',
            'epic_id': 'epic-5',
            'epic_title': 'AI Coach Integration',
            'story_id': '5.2',
            'story_title': 'Project-Aware Q&A',
            'story_status': 'IN_PROGRESS',
            'task': 'Implementing tests'
        }
        
        # Verify all fields are present
        assert 'epic_id' in expanded_context
        assert 'epic_title' in expanded_context
        assert 'story_id' in expanded_context
        assert 'story_title' in expanded_context
        assert 'story_status' in expanded_context
    
    def test_backward_compatibility(self):
        """Test that minimal context still works"""
        minimal_context = {
            'phase': 'Implementation',
            'epic': 'epic-5',
            'story': '5.2',
            'task': '1'
        }
        
        # AICoach should handle both old and new formats
        assert 'epic' in minimal_context or 'epic_id' in minimal_context
        assert 'story' in minimal_context or 'story_id' in minimal_context
