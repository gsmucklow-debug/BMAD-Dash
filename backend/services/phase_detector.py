"""
BMAD Dash - Phase Detection Service
Detects current BMAD project phase based on workflow status
"""
import os


class PhaseDetector:
    """
    Detects current BMAD phase based on presence of specific artifacts
    """
    
    @staticmethod
    def detect_phase(root_path: str) -> str:
        """
        Determines current project phase based on artifact presence
        
        Args:
            root_path: Path to project root directory
            
        Returns:
            Phase string: "Analysis" | "Planning" | "Solutioning" | "Implementation" | "Unknown"
            
        Detection logic:
        1. Check for sprint-status.yaml → "Implementation"
        2. Check for architecture.md without sprint-status → "Solutioning"
        3. Check for prd.md without architecture → "Planning"
        4. Check for brainstorming files only → "Analysis"
        5. Default to "Unknown"
        """
        if not root_path or not os.path.exists(root_path):
            return "Unknown"
        
        # Define artifact paths
        bmad_output = os.path.join(root_path, "_bmad-output")
        planning_artifacts = os.path.join(bmad_output, "planning-artifacts")
        implementation_artifacts = os.path.join(bmad_output, "implementation-artifacts")
        
        # Check for Implementation phase (sprint-status.yaml exists)
        sprint_status_paths = [
            os.path.join(implementation_artifacts, "sprint-status.yaml"),
            os.path.join(bmad_output, "sprint-status.yaml"),
            os.path.join(root_path, "sprint-status.yaml")
        ]
        
        for path in sprint_status_paths:
            if os.path.exists(path):
                return "Implementation"
        
        # Check for Solutioning phase (architecture.md exists)
        architecture_paths = [
            os.path.join(planning_artifacts, "architecture.md"),
            os.path.join(bmad_output, "architecture.md"),
            os.path.join(root_path, "architecture.md")
        ]
        
        for path in architecture_paths:
            if os.path.exists(path):
                return "Solutioning"
        
        # Check for Planning phase (prd.md exists)
        prd_paths = [
            os.path.join(planning_artifacts, "prd.md"),
            os.path.join(bmad_output, "prd.md"),
            os.path.join(root_path, "prd.md")
        ]
        
        for path in prd_paths:
            if os.path.exists(path):
                return "Planning"
        
        # Check for Analysis phase (brainstorming or product-brief)
        analysis_files = [
            "brainstorming.md",
            "product-brief.md",
            "ideas.md"
        ]
        
        for filename in analysis_files:
            check_paths = [
                os.path.join(planning_artifacts, filename),
                os.path.join(bmad_output, filename),
                os.path.join(root_path, filename)
            ]
            for path in check_paths:
                if os.path.exists(path):
                    return "Analysis"
        
        # No recognizable pattern
        return "Unknown"
    
    @staticmethod
    def detect_phase_from_data(project_data: dict) -> str:
        """
        Determines phase from parsed project data (alternative method)
        
        Args:
            project_data: Dictionary with project artifacts data
            
        Returns:
            Phase string
        """
        # Check for sprint_status data
        if project_data.get("sprint_status"):
            return "Implementation"
        
        # Check for architecture data
        if project_data.get("architecture"):
            return "Solutioning"
        
        # Check for PRD data
        if project_data.get("prd"):
            return "Planning"
        
        # Check for brainstorming data
        if project_data.get("brainstorming") or project_data.get("product_brief"):
            return "Analysis"
        
        return "Unknown"

