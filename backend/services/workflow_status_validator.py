"""
Workflow Status Validator

Validates bmm-workflow-status.yaml files against the proper BMAD Method structure.
Detects malformed or missing workflow tracking files and provides actionable feedback.
"""

import os
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
import yaml

logger = logging.getLogger(__name__)


class WorkflowStatusValidation:
    """Result of workflow status validation"""

    def __init__(self, is_valid: bool, errors: List[str], warnings: List[str],
                 suggestions: List[str], file_path: Optional[str] = None):
        self.is_valid = is_valid
        self.errors = errors
        self.warnings = warnings
        self.suggestions = suggestions
        self.file_path = file_path

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_valid": self.is_valid,
            "errors": self.errors,
            "warnings": self.warnings,
            "suggestions": self.suggestions,
            "file_path": self.file_path
        }


class WorkflowStatusValidator:
    """
    Validates bmm-workflow-status.yaml files to ensure they follow
    the proper BMAD Method structure.
    """

    # Required top-level fields in workflow-status.yaml
    REQUIRED_FIELDS = [
        "generated",
        "project",
        "project_type",
        "selected_track",
        "field_type",
        "workflow_path",
        "workflow_status"
    ]

    # Valid values for specific fields
    VALID_PROJECT_TYPES = ["greenfield", "brownfield"]
    VALID_TRACKS = ["bmad-method", "enterprise-method"]
    VALID_FIELD_TYPES = ["greenfield", "brownfield"]

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)

    def validate(self) -> WorkflowStatusValidation:
        """
        Validate the workflow-status file for this project.

        Returns:
            WorkflowStatusValidation with results and suggestions
        """
        errors = []
        warnings = []
        suggestions = []

        # Find workflow-status file
        workflow_file = self._find_workflow_status_file()

        if not workflow_file:
            errors.append("No bmm-workflow-status.yaml file found")
            suggestions.append("Run /bmad:bmm:workflows:workflow-init to initialize project tracking")
            return WorkflowStatusValidation(
                is_valid=False,
                errors=errors,
                warnings=warnings,
                suggestions=suggestions,
                file_path=None
            )

        # Load and parse YAML
        try:
            with open(workflow_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            errors.append(f"Invalid YAML syntax: {str(e)}")
            return WorkflowStatusValidation(
                is_valid=False,
                errors=errors,
                warnings=warnings,
                suggestions=suggestions,
                file_path=str(workflow_file)
            )
        except Exception as e:
            errors.append(f"Could not read file: {str(e)}")
            return WorkflowStatusValidation(
                is_valid=False,
                errors=errors,
                warnings=warnings,
                suggestions=suggestions,
                file_path=str(workflow_file)
            )

        if not isinstance(data, dict):
            errors.append("Workflow status file must be a YAML dictionary")
            suggestions.append("Run /bmad:bmm:workflows:workflow-init to regenerate the file")
            return WorkflowStatusValidation(
                is_valid=False,
                errors=errors,
                warnings=warnings,
                suggestions=suggestions,
                file_path=str(workflow_file)
            )

        # Check for required fields
        missing_fields = []
        for field in self.REQUIRED_FIELDS:
            if field not in data:
                missing_fields.append(field)

        if missing_fields:
            errors.append(f"Missing required fields: {', '.join(missing_fields)}")
            suggestions.append("This file appears to be malformed or outdated")
            suggestions.append("Run /bmad:bmm:workflows:workflow-init to regenerate the file")

        # Validate field values
        if "project_type" in data and data["project_type"] not in self.VALID_PROJECT_TYPES:
            warnings.append(f"Invalid project_type: {data['project_type']}")

        if "selected_track" in data and data["selected_track"] not in self.VALID_TRACKS:
            warnings.append(f"Invalid selected_track: {data['selected_track']}")

        if "field_type" in data and data["field_type"] not in self.VALID_FIELD_TYPES:
            warnings.append(f"Invalid field_type: {data['field_type']}")

        # Validate workflow_status structure
        if "workflow_status" in data:
            workflow_status = data["workflow_status"]

            if not isinstance(workflow_status, list):
                errors.append("workflow_status must be a list of phases")
            else:
                # Validate each phase
                for i, phase in enumerate(workflow_status):
                    if not isinstance(phase, dict):
                        errors.append(f"Phase {i} is not a dictionary")
                        continue

                    if "phase" not in phase:
                        errors.append(f"Phase {i} is missing 'phase' field")

                    if "name" not in phase:
                        errors.append(f"Phase {i} is missing 'name' field")

                    if "workflows" not in phase:
                        errors.append(f"Phase {i} is missing 'workflows' field")
                    elif not isinstance(phase["workflows"], list):
                        errors.append(f"Phase {i} workflows must be a list")
                    else:
                        # Validate each workflow in the phase
                        for j, workflow in enumerate(phase["workflows"]):
                            if not isinstance(workflow, dict):
                                errors.append(f"Phase {i}, workflow {j} is not a dictionary")
                                continue

                            required_workflow_fields = ["id", "name", "agent", "command", "status"]
                            for field in required_workflow_fields:
                                if field not in workflow:
                                    warnings.append(
                                        f"Phase {i}, workflow {j} ({workflow.get('name', 'unknown')}) "
                                        f"is missing '{field}' field"
                                    )

        # Determine overall validity
        is_valid = len(errors) == 0

        # Add helpful suggestions if invalid
        if not is_valid:
            if not suggestions:
                suggestions.append("Run /bmad:bmm:workflows:workflow-init to fix this file")

        return WorkflowStatusValidation(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            suggestions=suggestions,
            file_path=str(workflow_file)
        )

    def _find_workflow_status_file(self) -> Optional[Path]:
        """
        Find the bmm-workflow-status.yaml file in expected locations.

        Returns:
            Path to the file or None if not found
        """
        # Standard location
        standard_path = self.project_root / "_bmad-output" / "planning-artifacts" / "bmm-workflow-status.yaml"
        if standard_path.exists():
            return standard_path

        # Alternative location (older projects)
        alt_path = self.project_root / "_bmad-output" / "bmm-workflow-status.yaml"
        if alt_path.exists():
            return alt_path

        return None
