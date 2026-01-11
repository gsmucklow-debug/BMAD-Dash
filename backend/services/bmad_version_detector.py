"""
BMAD Dash - BMAD Version Detector Service
Detects BMAD Method version from project artifacts
"""

import os
import yaml
from typing import Optional


class BMADVersionDetector:
    """
    Detects BMAD Method version from project configuration and artifacts
    """
    
    def __init__(self, project_root: str):
        """
        Initialize version detector
        
        Args:
            project_root: Root directory of the project
        """
        self.project_root = project_root
        self._cached_version: Optional[str] = None
    
    def detect_version(self) -> str:
        """
        Detect BMAD Method version from project files
        
        Returns:
            Version string (e.g., "1.0.0") or "latest" if not found
        """
        if self._cached_version:
            return self._cached_version
        
        # Check sprint-status.yaml for version field
        version = self._check_sprint_status()
        if version:
            self._cached_version = version
            return version
        
        # Check workflow.yaml files
        version = self._check_workflow_files()
        if version:
            self._cached_version = version
            return version
        
        # Check epics.md or other artifacts for version hints
        version = self._check_artifacts()
        if version:
            self._cached_version = version
            return version
        
        # Default to latest
        self._cached_version = "latest"
        return "latest"
    
    def _check_sprint_status(self) -> Optional[str]:
        """Check sprint-status.yaml for bmad_version field"""
        sprint_status_paths = [
            os.path.join(self.project_root, '_bmad-output', 'implementation-artifacts', 'sprint-status.yaml'),
            os.path.join(self.project_root, 'sprint-status.yaml'),
        ]
        
        for path in sprint_status_paths:
            if os.path.exists(path):
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        data = yaml.safe_load(f)
                        if data and 'bmad_version' in data:
                            return str(data['bmad_version'])
                except Exception:
                    pass
        
        return None
    
    def _check_workflow_files(self) -> Optional[str]:
        """Check workflow.yaml files for version information"""
        workflow_paths = [
            os.path.join(self.project_root, '.agent', 'workflows', 'workflow.yaml'),
            os.path.join(self.project_root, '_bmad-output', 'workflow.yaml'),
        ]
        
        for path in workflow_paths:
            if os.path.exists(path):
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        data = yaml.safe_load(f)
                        if data and 'bmad_version' in data:
                            return str(data['bmad_version'])
                except Exception:
                    pass
        
        return None
    
    def _check_artifacts(self) -> Optional[str]:
        """Check artifacts directory for version hints"""
        # Could scan epics.md or other files for version metadata
        # For now, return None
        return None
    
    def invalidate_cache(self):
        """Invalidate cached version (call when project files change)"""
        self._cached_version = None
    
    def get_version_info(self) -> dict:
        """
        Get detailed version information
        
        Returns:
            Dictionary with version and detection method
        """
        version = self.detect_version()
        return {
            'version': version,
            'is_latest': version == 'latest',
            'detected_from': self._get_detection_source()
        }
    
    def _get_detection_source(self) -> str:
        """Get the source where version was detected from"""
        if self._check_sprint_status():
            return 'sprint-status.yaml'
        elif self._check_workflow_files():
            return 'workflow.yaml'
        else:
            return 'default'
