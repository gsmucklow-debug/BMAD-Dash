"""
BMAD Dash - Phase Detection Tests
Tests for phase detection algorithm
"""
import pytest
import os
from backend.services.phase_detector import PhaseDetector


class TestPhaseDetection:
    """Test phase detection logic"""
    story_id = "1.2"
    
    def test_detect_implementation_phase(self, tmp_path):
        """Test detecting Implementation phase"""
        # Create BMAD structure with sprint-status.yaml
        impl_artifacts = tmp_path / "_bmad-output" / "implementation-artifacts"
        impl_artifacts.mkdir(parents=True)
        
        sprint_status = impl_artifacts / "sprint-status.yaml"
        sprint_status.write_text("project_name: Test")
        
        phase = PhaseDetector.detect_phase(str(tmp_path))
        
        assert phase == "Implementation"
    
    def test_detect_solutioning_phase(self, tmp_path):
        """Test detecting Solutioning phase"""
        # Create BMAD structure with architecture.md but no sprint-status
        planning_artifacts = tmp_path / "_bmad-output" / "planning-artifacts"
        planning_artifacts.mkdir(parents=True)
        
        architecture = planning_artifacts / "architecture.md"
        architecture.write_text("# Architecture")
        
        phase = PhaseDetector.detect_phase(str(tmp_path))
        
        assert phase == "Solutioning"
    
    def test_detect_planning_phase(self, tmp_path):
        """Test detecting Planning phase"""
        # Create BMAD structure with prd.md but no architecture
        planning_artifacts = tmp_path / "_bmad-output" / "planning-artifacts"
        planning_artifacts.mkdir(parents=True)
        
        prd = planning_artifacts / "prd.md"
        prd.write_text("# PRD")
        
        phase = PhaseDetector.detect_phase(str(tmp_path))
        
        assert phase == "Planning"
    
    def test_detect_analysis_phase(self, tmp_path):
        """Test detecting Analysis phase"""
        # Create BMAD structure with brainstorming file
        planning_artifacts = tmp_path / "_bmad-output" / "planning-artifacts"
        planning_artifacts.mkdir(parents=True)
        
        brainstorming = planning_artifacts / "brainstorming.md"
        brainstorming.write_text("# Ideas")
        
        phase = PhaseDetector.detect_phase(str(tmp_path))
        
        assert phase == "Analysis"
    
    def test_detect_analysis_with_product_brief(self, tmp_path):
        """Test detecting Analysis phase with product-brief"""
        planning_artifacts = tmp_path / "_bmad-output" / "planning-artifacts"
        planning_artifacts.mkdir(parents=True)
        
        product_brief = planning_artifacts / "product-brief.md"
        product_brief.write_text("# Product Brief")
        
        phase = PhaseDetector.detect_phase(str(tmp_path))
        
        assert phase == "Analysis"
    
    def test_detect_unknown_phase(self, tmp_path):
        """Test detecting Unknown phase when no artifacts exist"""
        phase = PhaseDetector.detect_phase(str(tmp_path))
        
        assert phase == "Unknown"
    
    def test_detect_unknown_for_nonexistent_path(self):
        """Test Unknown phase for non-existent path"""
        phase = PhaseDetector.detect_phase("/nonexistent/path")
        
        assert phase == "Unknown"
    
    def test_detect_unknown_for_empty_path(self):
        """Test Unknown phase for empty path"""
        phase = PhaseDetector.detect_phase("")
        
        assert phase == "Unknown"
    
    def test_phase_priority_implementation_over_solutioning(self, tmp_path):
        """Test Implementation takes priority over Solutioning"""
        # Create both sprint-status and architecture
        bmad_output = tmp_path / "_bmad-output"
        impl_artifacts = bmad_output / "implementation-artifacts"
        planning_artifacts = bmad_output / "planning-artifacts"
        impl_artifacts.mkdir(parents=True)
        planning_artifacts.mkdir(parents=True)
        
        sprint_status = impl_artifacts / "sprint-status.yaml"
        sprint_status.write_text("project: test")
        
        architecture = planning_artifacts / "architecture.md"
        architecture.write_text("# Architecture")
        
        phase = PhaseDetector.detect_phase(str(tmp_path))
        
        # Implementation should win
        assert phase == "Implementation"
    
    def test_phase_priority_solutioning_over_planning(self, tmp_path):
        """Test Solutioning takes priority over Planning"""
        planning_artifacts = tmp_path / "_bmad-output" / "planning-artifacts"
        planning_artifacts.mkdir(parents=True)
        
        # Create both architecture and PRD
        architecture = planning_artifacts / "architecture.md"
        architecture.write_text("# Architecture")
        
        prd = planning_artifacts / "prd.md"
        prd.write_text("# PRD")
        
        phase = PhaseDetector.detect_phase(str(tmp_path))
        
        # Solutioning should win
        assert phase == "Solutioning"
    
    def test_phase_priority_planning_over_analysis(self, tmp_path):
        """Test Planning takes priority over Analysis"""
        planning_artifacts = tmp_path / "_bmad-output" / "planning-artifacts"
        planning_artifacts.mkdir(parents=True)
        
        # Create both PRD and brainstorming
        prd = planning_artifacts / "prd.md"
        prd.write_text("# PRD")
        
        brainstorming = planning_artifacts / "brainstorming.md"
        brainstorming.write_text("# Ideas")
        
        phase = PhaseDetector.detect_phase(str(tmp_path))
        
        # Planning should win
        assert phase == "Planning"
    
    def test_detect_phase_from_data_implementation(self):
        """Test detect_phase_from_data for Implementation"""
        project_data = {
            "sprint_status": {"epics": []},
            "architecture": {},
            "prd": {}
        }
        
        phase = PhaseDetector.detect_phase_from_data(project_data)
        
        assert phase == "Implementation"
    
    def test_detect_phase_from_data_solutioning(self):
        """Test detect_phase_from_data for Solutioning"""
        project_data = {
            "architecture": {"decisions": []},
            "prd": {}
        }
        
        phase = PhaseDetector.detect_phase_from_data(project_data)
        
        assert phase == "Solutioning"
    
    def test_detect_phase_from_data_planning(self):
        """Test detect_phase_from_data for Planning"""
        project_data = {
            "prd": {"requirements": []}
        }
        
        phase = PhaseDetector.detect_phase_from_data(project_data)
        
        assert phase == "Planning"
    
    def test_detect_phase_from_data_analysis(self):
        """Test detect_phase_from_data for Analysis"""
        project_data = {
            "brainstorming": {"ideas": []}
        }
        
        phase = PhaseDetector.detect_phase_from_data(project_data)
        
        assert phase == "Analysis"
    
    def test_detect_phase_from_data_unknown(self):
        """Test detect_phase_from_data for Unknown"""
        project_data = {}
        
        phase = PhaseDetector.detect_phase_from_data(project_data)
        
        assert phase == "Unknown"
    
    def test_alternative_artifact_locations(self, tmp_path):
        """Test detecting artifacts in alternative locations"""
        # Test sprint-status in bmad_output root
        bmad_output = tmp_path / "_bmad-output"
        bmad_output.mkdir()
        
        sprint_status = bmad_output / "sprint-status.yaml"
        sprint_status.write_text("project: test")
        
        phase = PhaseDetector.detect_phase(str(tmp_path))
        
        assert phase == "Implementation"
    
    def test_artifact_in_project_root(self, tmp_path):
        """Test detecting artifacts in project root"""
        # Some projects might have artifacts in root
        architecture = tmp_path / "architecture.md"
        architecture.write_text("# Architecture")
        
        phase = PhaseDetector.detect_phase(str(tmp_path))
        
        assert phase == "Solutioning"


class TestPhaseDetectionPerformance:
    """Test phase detection performance requirements"""
    
    def test_phase_detection_performance(self, tmp_path):
        """Test phase detection completes in <100ms (NFR3 requirement)"""
        import time
        
        # Create typical BMAD structure
        impl_artifacts = tmp_path / "_bmad-output" / "implementation-artifacts"
        impl_artifacts.mkdir(parents=True)
        
        sprint_status = impl_artifacts / "sprint-status.yaml"
        sprint_status.write_text("project: test")
        
        # Measure execution time
        start = time.time()
        phase = PhaseDetector.detect_phase(str(tmp_path))
        elapsed = (time.time() - start) * 1000  # Convert to ms
        
        assert phase == "Implementation"
        assert elapsed < 100, f"Phase detection took {elapsed}ms, requirement is <100ms"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
