"""
BMAD Dash - AI Coach Service
Integrates Gemini 3 Flash for contextual guidance
"""

import google.generativeai as genai
from typing import Generator, Dict, Any, Optional
import json
import os
from backend.services.bmad_version_detector import BMADVersionDetector
from backend.services.validation_service import ValidationService
from backend.services.project_state_cache import ProjectStateCache


class AICoach:
    """
    AI-powered contextual guidance using Gemini 3 Flash
    Provides streaming responses for real-time chat experience
    """
    
    def __init__(self, api_key: str, project_root: str = None):
        """
        Initialize the AI Coach with Gemini API key

        Args:
            api_key: Gemini API key from environment
            project_root: Optional project root for BMAD version detection
        """
        self.api_key = api_key
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        self.version_detector = BMADVersionDetector(project_root) if project_root else None
        self.validation_service = ValidationService(project_root) if project_root else None
        
        # Initialize ProjectStateCache (Story 5.4)
        self.project_state_cache = None
        if project_root:
            cache_file = os.path.join(project_root, "_bmad-output/implementation-artifacts/project-state.json")
            self.project_state_cache = ProjectStateCache(cache_file)
            
        self.project_root = project_root
    
    def _format_validation_summary(self, validation_result) -> str:
        """
        Format validation result into human-readable summary (Story 5.3 AC2, AC4)

        Args:
            validation_result: ValidationResult object

        Returns:
            Formatted validation summary string
        """
        if validation_result.is_complete:
            # Story appears complete
            evidence_list = []
            if validation_result.has_git_commits:
                last_commit = validation_result.git_last_commit_time
                time_str = last_commit.strftime("%Y-%m-%d %H:%M") if last_commit else "unknown"
                evidence_list.append(f"✅ **Git Evidence**: {validation_result.git_commit_count} commits (last: {time_str})")

            if validation_result.has_tests:
                last_run = validation_result.test_last_run_time
                if last_run:
                    from datetime import datetime
                    age = datetime.now() - last_run.replace(tzinfo=None) if last_run.tzinfo else datetime.now() - last_run
                    hours_ago = int(age.total_seconds() / 3600)
                    time_str = f"{hours_ago}h ago" if hours_ago > 0 else "recently"
                else:
                    time_str = "unknown"
                evidence_list.append(f"✅ **Test Evidence**: {validation_result.test_pass_count}/{validation_result.test_pass_count + validation_result.test_fail_count} tests passing (last run: {time_str})")

            if validation_result.all_tasks_complete:
                evidence_list.append(f"✅ **Tasks**: All tasks complete")

            if validation_result.has_dev_story_workflow:
                evidence_list.append(f"✅ **Workflow**: dev-story executed")

            if validation_result.has_code_review_workflow:
                evidence_list.append(f"✅ **Workflow**: code-review executed")

            summary = f"**Story {validation_result.story_id} appears complete:**\n" + "\n".join(evidence_list)
        else:
            # Story has issues
            summary = f"**Story {validation_result.story_id} marked done but issues found:**\n"
            for issue in validation_result.issues:
                summary += f"⚠️ {issue}\n"

            # Add suggested commands (Story 5.3 AC4)
            if not validation_result.has_dev_story_workflow:
                summary += f"\n**Suggestion**: Run `/bmad-bmm-workflows-dev-story`"
            elif not validation_result.has_code_review_workflow:
                summary += f"\n**Suggestion**: Run `/bmad-bmm-workflows-code-review`"

        return summary

    def _detect_validation_intent(self, message: str, context: Dict[str, Any]) -> Optional[str]:
        """
        Detect if user is asking for story validation (AC2, Story 5.3)

        Args:
            message: User's question
            context: Context with story_id

        Returns:
            Story ID to validate, or None if not a validation query
        """
        message_lower = message.lower()

        # Validation intent keywords
        validation_keywords = [
            'complete', 'completed', 'correctly', 'done',
            'validate', 'validation', 'check', 'verify',
            'did the ai', 'did agent', 'was story',
            'finished', 'ready'
        ]

        # Check if message contains validation intent
        has_validation_intent = any(keyword in message_lower for keyword in validation_keywords)

        if has_validation_intent:
            # Extract story ID from context or message
            story_id = context.get('story_id') or context.get('story')

            # Try to extract story ID from message (e.g., "Story 5.3", "5.3")
            import re
            story_match = re.search(r'\b(\d+)\.(\d+)\b', message)
            if story_match:
                story_id = f"{story_match.group(1)}.{story_match.group(2)}"

            return story_id

        return None

    def _build_system_prompt(self, context: Dict[str, Any]) -> str:
        """
        Constructs the system prompt with BMAD context and full Project State

        Args:
            context: Dictionary containing project context 

        Returns:
            System prompt string
        """
        # Load full project state if available (Story 5.4)
        project_state_context = ""
        if self.project_state_cache and self.project_root:
            try:
                # Sync to ensure we satisfy "all epics, all stories" requirement
                self.project_state_cache.sync(self.project_root)
                state = self.project_state_cache.cache_data
                if state:
                    state_dict = state.to_dict()
                    # Convert to JSON string for prompt
                    project_state_json = json.dumps(state_dict, indent=2)
                    project_state_context = f"\n\nFULL PROJECT STATE (Source of Truth):\n```json\n{project_state_json}\n```"
            except Exception as e:
                # Fallback to limited context if cache fails
                project_state_context = f"\n\nProject State Error: {str(e)}"

        phase = context.get('phase', 'Unknown')
        epic_id = context.get('epic_id', context.get('epic', 'Unknown'))
        # ... (rest of simple context extraction for fallback/immediate context) ...
        epic_title = context.get('epic_title', '')
        story_id = context.get('story_id', context.get('story', 'Unknown'))
        story_title = context.get('story_title', '')
        story_status = context.get('story_status', 'Unknown')
        task_progress = context.get('taskProgress', '0/0 tasks') # Fix definition order
        current_task = context.get('currentTask', 'No active task')
        current_task_status = context.get('currentTaskStatus', 'unknown')
        tasks = context.get('tasks', [])
        acceptance_criteria = context.get('acceptanceCriteria', [])

        # Check if validation results should be included (Story 5.3 AC2)
        validation_summary = context.get('validation_summary', '')
        
        # Format task list for system prompt
        task_list_str = ""
        if tasks:
            done_tasks = [t for t in tasks if t.get('status') == 'done']
            task_list_str = f"\n\nTask Details ({len(done_tasks)}/{len(tasks)} complete):"
            for t in tasks:
                status_icon = "✓" if t.get('status') == 'done' else "○"
                task_list_str += f"\n  {status_icon} {t.get('title', 'Unknown task')} [{t.get('status', 'unknown')}]"
        
        # Format acceptance criteria
        ac_str = ""
        if acceptance_criteria:
            ac_str = "\n\nAcceptance Criteria Summary:"
            for ac in acceptance_criteria[:5]:  # Limit to first 5
                ac_str += f"\n  - {ac}"
        
        # Get BMAD version info
        bmad_version = "latest"
        if self.version_detector:
            bmad_version = self.version_detector.detect_version()
        
        # Format validation summary if present (Story 5.3 AC2)
        validation_context = ""
        if validation_summary:
            validation_context = f"\n\n**Story Validation Results:**\n{validation_summary}"

        system_prompt = f"""You are the BMAD (Brain-Friendly Method for AI Development) Coach AI assistant.

BMAD Method Version: {bmad_version}

You help developers working on BMAD projects by providing contextual guidance based on their current project state.

Current Project Context:
- Phase: {phase}
- Epic: {epic_id}{' - ' + epic_title if epic_title else ''}
- Story: {story_id}{' - ' + story_title if story_title else ''}
- Story Status: {story_status}
- Task Progress: {task_progress}
- Current Task: {current_task} [{current_task_status}]{task_list_str}{ac_str}{validation_context}
{project_state_context}

BMAD Method Principles:
1. Brain-Friendly Design: Minimize cognitive load, use progressive disclosure
2. Validation-Driven: Verify AI agent work through Git commits and test results
3. Zero-Friction Execution: One-click command copying, clear next steps
4. Multi-View Adaptation: Support different cognitive states (Dashboard, Timeline, List)

Your Role:
- Provide project-aware answers based on current phase, epic, story, and task
- Suggest appropriate BMAD workflows based on story state
- Help validate AI agent outputs by comparing claims vs. Git/test evidence
- Detect workflow gaps and suggest corrective actions
- Reference BMAD Method documentation when providing guidance

Response Guidelines:
- Be concise and actionable
- Format code blocks with proper syntax highlighting
- When suggesting commands, provide copy-paste ready format
- If you don't know something specific about the project, acknowledge it
- Maintain conversation context across multiple turns

BMAD Workflow Suggestions:
When user asks "What should I do next?", analyze the current story status and suggest:
- If status is "TODO" or "READY_FOR_DEV" → Suggest: `/bmad-bmm-workflows-dev-story {story_id}`
  Explanation: "Start development on this story by running the dev-story workflow."
  
- If status is "IN_PROGRESS" → Check progress:
  - If tasks incomplete → Suggest: "Continue implementing the remaining tasks"
  - If tasks complete → Suggest: `/bmad-bmm-workflows-code-review {story_id}`
  Explanation: "Run the code-review workflow to validate your implementation."
  
- If status is "REVIEW" → Suggest: `/bmad-bmm-workflows-code-review {story_id}`
  Explanation: "Run the adversarial code review to find and fix any issues."
  
- If status is "DONE" or "COMPLETE" → Suggest creating the next story or retrospective
  Explanation: "This story is complete. Consider creating the next story or running a retrospective."

When providing workflow commands, always format them as:
```
/bmad-bmm-workflows-[workflow-name] [story-id]
```

When validating agent work:
- Check Git commits exist for the story
- Check tests were run and passed
- Verify all tasks are marked complete
- Check if code-review workflow was executed

Remember: You have access to the current project state, so reference it in your responses. For example:
- "Your current story is {story_id}..."
- "Since you're in the {phase} phase..."
- "Epic {epic_id} is focused on..."
"""
        return system_prompt
    
    def generate_stream(self, message: str, context: Dict[str, Any]) -> Generator[str, None, None]:
        """
        Generates streaming AI response using Gemini 3 Flash

        Args:
            message: User's question or prompt
            context: Dictionary containing project context (phase, epic, story, task)

        Yields:
            JSON-formatted SSE data chunks with token content

        Raises:
            ValueError: If API key is not configured
            genai.APIError: If Gemini API call fails
        """
        if not self.api_key or self.api_key == 'your-api-key-here':
            raise ValueError("GEMINI_API_KEY is not configured. Please set it in .env file")

        try:
            # Detect validation intent (Story 5.3 AC1, AC2)
            validation_story_id = self._detect_validation_intent(message, context)

            if validation_story_id and self.validation_service:
                # Run validation
                validation_result = self.validation_service.validate_story(validation_story_id)

                # Format validation summary (Story 5.3 AC2)
                validation_summary = self._format_validation_summary(validation_result)

                # Add validation summary to context
                context['validation_summary'] = validation_summary

            system_prompt = self._build_system_prompt(context)
            
            # Combine system prompt with user message
            full_prompt = f"{system_prompt}\n\nUser: {message}"
            
            # Generate streaming response
            response = self.model.generate_content(
                full_prompt,
                stream=True,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    top_p=0.9,
                    max_output_tokens=2048,
                )
            )
            
            # Stream tokens as SSE format
            for chunk in response:
                if chunk.text:
                    # Format as SSE: data: {"token": "..."}
                    sse_data = json.dumps({"token": chunk.text})
                    yield f"data: {sse_data}\n\n"
                    
        except Exception as e:
            # Handle any errors (google.generativeai may not have APIError class)
            error_msg = json.dumps({"error": str(e)})
            yield f"data: {error_msg}\n\n"
    
    def get_response(self, message: str, context: Dict[str, Any]) -> str:
        """
        Gets non-streaming AI response (for backward compatibility)
        
        Args:
            message: User's question or prompt
            context: Dictionary containing project context (phase, epic, story, task)
            
        Returns:
            Complete AI response as string
        """
        if not self.api_key or self.api_key == 'your-api-key-here':
            raise ValueError("GEMINI_API_KEY is not configured. Please set it in .env file")
        
        try:
            system_prompt = self._build_system_prompt(context)
            full_prompt = f"{system_prompt}\n\nUser: {message}"
            
            response = self.model.generate_content(full_prompt)
            return response.text
            
        except Exception as e:
            # Handle any errors (google.generativeai may not have APIError class)
            return f"Error: {str(e)}"
