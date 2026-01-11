"""
BMAD Dash - AI Coach Service
Integrates Gemini 3 Flash for contextual guidance
"""

import google.generativeai as genai
from typing import Generator, Dict, Any, Optional
import json


class AICoach:
    """
    AI-powered contextual guidance using Gemini 3 Flash
    Provides streaming responses for real-time chat experience
    """
    
    def __init__(self, api_key: str):
        """
        Initialize the AI Coach with Gemini API key
        
        Args:
            api_key: Gemini API key from environment
        """
        self.api_key = api_key
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
    
    def _build_system_prompt(self, context: Dict[str, Any]) -> str:
        """
        Constructs the system prompt with BMAD context
        
        Args:
            context: Dictionary containing project context (phase, epic, story, task)
            
        Returns:
            System prompt string
        """
        phase = context.get('phase', 'Unknown')
        epic = context.get('epic', 'Unknown')
        story = context.get('story', 'Unknown')
        task = context.get('task', 'Unknown')
        
        system_prompt = f"""You are the BMAD (Brain-Friendly Method for AI Development) Coach AI assistant.

You help developers working on BMAD projects by providing contextual guidance based on their current project state.

Current Project Context:
- Phase: {phase}
- Epic: {epic}
- Story: {story}
- Task: {task}

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

When asked "What should I do next?":
- Analyze current story state
- Suggest the correct BMAD workflow command
- Explain why this is the next step in the sequence

When validating agent work:
- Check Git commits exist for the story
- Check tests were run and passed
- Verify all tasks are marked complete
- Check if code-review workflow was executed
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
