"""
BMAD Dash - AI Coach Service
Integrates Gemini 3 Flash for contextual guidance
"""

import google.generativeai as genai
from typing import Generator, Dict, Any, Optional
import json
from backend.services.bmad_version_detector import BMADVersionDetector


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
    
    def _build_system_prompt(self, context: Dict[str, Any]) -> str:
        """
        Constructs the system prompt with BMAD context
        
        Args:
            context: Dictionary containing project context (phase, epic, story, task, status, titles, tasks)
            
        Returns:
            System prompt string
        """
        phase = context.get('phase', 'Unknown')
        epic_id = context.get('epic_id', context.get('epic', 'Unknown'))
        epic_title = context.get('epic_title', '')
        story_id = context.get('story_id', context.get('story', 'Unknown'))
        story_title = context.get('story_title', '')
        story_status = context.get('story_status', 'Unknown')
        task = context.get('task', 'Unknown')
        
        # Task-level details (Story 5.2 AC4)
        task_progress = context.get('taskProgress', '0/0 tasks')
        current_task = context.get('currentTask', 'No active task')
        current_task_status = context.get('currentTaskStatus', 'unknown')
        tasks = context.get('tasks', [])
        acceptance_criteria = context.get('acceptanceCriteria', [])
        
        # Format task list for system prompt
        task_list_str = ""
        if tasks:
            done_tasks = [t for t in tasks if t.get('status') == 'done']
            todo_tasks = [t for t in tasks if t.get('status') in ['todo', 'in-progress']]
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
        
        system_prompt = f"""You are the BMAD (Brain-Friendly Method for AI Development) Coach AI assistant.

BMAD Method Version: {bmad_version}

You help developers working on BMAD projects by providing contextual guidance based on their current project state.

Current Project Context:
- Phase: {phase}
- Epic: {epic_id}{' - ' + epic_title if epic_title else ''}
- Story: {story_id}{' - ' + story_title if story_title else ''}
- Story Status: {story_status}
- Task Progress: {task_progress}
- Current Task: {current_task} [{current_task_status}]{task_list_str}{ac_str}

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
