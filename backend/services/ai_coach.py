"""
BMAD Dash - AI Coach Service
Integrates Gemini 3 Flash for contextual guidance
"""

import google.generativeai as genai
from typing import Generator, Dict, Any, Optional
import json
import os
import logging
import re
from pathlib import Path
import requests
from bs4 import BeautifulSoup
from backend.services.bmad_version_detector import BMADVersionDetector
from backend.services.validation_service import ValidationService
from backend.services.project_state_cache import ProjectStateCache
from backend.services.story_detail_fetcher import StoryDetailFetcher
from backend.config import Config

logger = logging.getLogger(__name__)


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
        self.model = genai.GenerativeModel('gemini-3-flash-preview')
        self.version_detector = BMADVersionDetector(project_root) if project_root else None
        self.validation_service = ValidationService(project_root) if project_root else None

        # Initialize ProjectStateCache (Story 5.4)
        self.project_state_cache = None
        if project_root:
            cache_file = os.path.join(project_root, "_bmad-output/implementation-artifacts/project-state.json")
            self.project_state_cache = ProjectStateCache(cache_file)

        # Initialize StoryDetailFetcher for detailed story lookups
        self.story_detail_fetcher = StoryDetailFetcher(project_root) if project_root else None

        self.project_root = project_root

        # Cache for BMAD documentation
        self._bmad_docs_cache = None
        self._bmad_docs_fetch_time = None

    def _fetch_bmad_docs(self, force: bool = False) -> Optional[str]:
        """
        Fetch BMAD documentation from docs.bmad-method.org

        Args:
            force: Force re-fetch even if cached

        Returns:
            Extracted text content from BMAD docs or None if fetch fails
        """
        from datetime import datetime, timedelta

        # Return cached docs if available and recent (within 1 hour)
        if not force and self._bmad_docs_cache and self._bmad_docs_fetch_time:
            age = datetime.now() - self._bmad_docs_fetch_time
            if age < timedelta(hours=1):
                logger.info("Returning cached BMAD docs")
                return self._bmad_docs_cache

        try:
            docs_url = getattr(Config, 'BMAD_DOCS_URL', 'http://docs.bmad-method.org')
            logger.info(f"Fetching BMAD documentation from {docs_url}")
            response = requests.get(
                docs_url,
                timeout=10,
                headers={'User-Agent': 'BMAD-Dash/1.0'}
            )
            response.raise_for_status()

            # Parse HTML and extract main content safely (Fix #2: Fragile Parsing)
            soup = BeautifulSoup(response.text, 'html.parser')

            # Naive tag removal can be fragile if site structure changes.
            # Instead, just extract text from body, assuming the LLM can handle some noise.
            # But we still try to focus on 'main' or 'article' if present to be cleaner.
            content_area = soup.find('main') or soup.find('article') or soup.body or soup

            # Get text content
            text = content_area.get_text(separator='\n', strip=True)

            # Clean up multiple blank lines
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            cleaned_text = '\n'.join(lines)

            # Limit to reasonable size with semantic truncation (Fix #3: Semantic Truncation)
            MAX_CHARS = 8000
            if len(cleaned_text) > MAX_CHARS:
                # Find last newline within the limit to avoid cutting sentences/code
                truncation_point = cleaned_text.rfind('\n', 0, MAX_CHARS)
                if truncation_point == -1:
                    truncation_point = MAX_CHARS # Fallback if no newline found

                cleaned_text = cleaned_text[:truncation_point] + "\n\n... (documentation truncated for brevity)"

            # Cache the result
            self._bmad_docs_cache = cleaned_text
            self._bmad_docs_fetch_time = datetime.now()

            logger.info(f"Successfully fetched BMAD docs: {len(cleaned_text)} chars")
            return cleaned_text

        except Exception as e:
            logger.error(f"Failed to fetch BMAD documentation: {e}")
            return None

    def _detect_bmad_methodology_question(self, message: str) -> bool:
        """
        Detect if user is asking about BMAD methodology, principles, or concepts

        Args:
            message: User's question

        Returns:
            True if question is about BMAD methodology
        """
        message_lower = message.lower()
        bmad_keywords = [
            'bmad method', 'bmad principle', 'bmad workflow', 'bmad process',
            'what is bmad', 'how does bmad', 'bmad approach', 'bmad methodology',
            'bmad concept', 'bmad practice', 'bmad framework', 'bmad documentation'
        ]
        return any(keyword in message_lower for keyword in bmad_keywords)
    
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
                summary += f"\n**Suggestion**: Run `/bmad:bmm:workflows:dev-story`"
            elif not validation_result.has_code_review_workflow:
                summary += f"\n**Suggestion**: Run `/bmad:bmm:workflows:code-review`"

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
            story_match = re.search(r'\b(\d+)\.(\d+)\b', message)
            if story_match:
                story_id = f"{story_match.group(1)}.{story_match.group(2)}"

            return story_id

        return None

    def _detect_story_query(self, message: str) -> Optional[str]:
        """
        Detect if user is asking about a specific story and extract story ID

        Args:
            message: User's question

        Returns:
            Story ID (e.g., "5.2") or None if no story query detected
        """
        # Pattern: "story 5.2", "Story 5.2", "5.2", etc.
        story_match = re.search(r'(?:story\s+)?(\d+)\.(\d+)', message, re.IGNORECASE)
        if story_match:
            return f"{story_match.group(1)}.{story_match.group(2)}"
        return None

    def _inject_story_details(self, message: str, system_prompt: str) -> str:
        """
        Detect if user is asking about a story and inject full details into system prompt

        Args:
            message: User's question
            system_prompt: Current system prompt

        Returns:
            Enhanced system prompt with story details
        """
        if not self.story_detail_fetcher:
            return system_prompt

        story_id = self._detect_story_query(message)
        if not story_id:
            return system_prompt

        # Fetch detailed story information
        story_details = self.story_detail_fetcher.get_story_details(story_id)
        if not story_details:
            return system_prompt

        # Format story details for injection
        details_section = f"\n\nREQUESTED STORY DETAILS (Story {story_id}):\n"
        details_section += f"Title: {story_details['title']}\n"
        details_section += f"Status: {story_details['status']}\n"
        details_section += f"Progress: {story_details['completed_tasks']}/{story_details['total_tasks']} tasks complete\n"

        if story_details['summary']:
            details_section += f"\nUser Story:\n{story_details['summary']}\n"

        if story_details['acceptance_criteria']:
            details_section += f"\nAcceptance Criteria:\n"
            for ac in story_details['acceptance_criteria']:
                details_section += f"  - {ac}\n"

        if story_details['tasks']:
            details_section += f"\nTasks:\n"
            for task in story_details['tasks']:
                status_icon = "✓" if task['status'] == 'done' else "○"
                details_section += f"  {status_icon} {task['title']} [{task['status']}]\n"

        return system_prompt + details_section

    def _get_local_bmad_docs(self) -> Optional[str]:
        """
        Read BMAD documentation from the local _bmad folder.
        Story 5.6: Prefer local docs over remote fetch.
        """
        if not self.project_root:
            return None
            
        bmad_dir = Path(self.project_root) / '_bmad'
        if not bmad_dir.exists() or not bmad_dir.is_dir():
            return None
            
        docs_content = []
        # BMAD structure: _bmad/core/*.md, _bmad/bmm/*.md
        for sub_dir in ['core', 'bmm']:
            path = bmad_dir / sub_dir
            if path.exists() and path.is_dir():
                for md_file in path.glob('**/*.md'):
                    try:
                        with open(md_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                            # Strip frontmatter
                            if content.startswith('---'):
                                end_idx = content.find('---', 3)
                                if end_idx != -1:
                                    content = content[end_idx+3:].strip()
                            
                            docs_content.append(f"### {md_file.name}\n{content}")
                    except Exception as e:
                        logger.warning(f"Failed to read local doc {md_file}: {e}")
                        
        if not docs_content:
            return None
            
        combined_docs = "\n\n".join(docs_content)
        
        # Limit size (roughly 12k chars for local docs)
        MAX_CHARS = 12000
        if len(combined_docs) > MAX_CHARS:
             truncation_point = combined_docs.rfind('\n', 0, MAX_CHARS)
             if truncation_point == -1: truncation_point = MAX_CHARS
             combined_docs = combined_docs[:truncation_point] + "\n\n... (local documentation truncated)"
             
        return combined_docs

    def _build_system_prompt(self, context: Dict[str, Any], bmad_docs: Optional[str] = None) -> str:
        """
        Constructs the system prompt with BMAD context and full Project State

        Args:
            context: Dictionary containing project context
            bmad_docs: Optional BMAD documentation content to inject

        Returns:
            System prompt string
        """
        # Load full project state if available (Story 5.4)
        project_state_context = ""
        current_root = context.get('project_root')
        
        # Determine effective project root: context > self.project_root
        effective_root = current_root if current_root else self.project_root
        
        # Lazily initialize or re-initialize cache if root changes or is missing
        if effective_root:
            normalized_effective = str(Path(effective_root).resolve())
            current_cache_root = ""
            if self.project_state_cache:
                current_cache_root = str(self.project_state_cache.cache_file.parent.parent.parent.resolve())
            
            if not self.project_state_cache or normalized_effective != current_cache_root:
                try:
                   cache_dir = os.path.join(effective_root, "_bmad-output", "implementation-artifacts")
                   cache_file = os.path.join(cache_dir, "project-state.json")
                   logger.info(f"AI Coach initializing ProjectStateCache for root: {effective_root}")
                   self.project_state_cache = ProjectStateCache(cache_file)
                except Exception as ex:
                   logger.error(f"AI Coach failed to init cache for {effective_root}: {ex}")

        if self.project_state_cache and effective_root:
            try:
                # Ensure data is loaded from file first
                if self.project_state_cache.cache_data is None:
                    self.project_state_cache.load()

                # Sync to ensure we satisfy "all epics, all stories" requirement
                self.project_state_cache.sync(effective_root)
                state = self.project_state_cache.cache_data
                if state:
                    project_state_context = f"\n\nPROJECT STATE SUMMARY:\n{self.project_state_cache.summarize_for_ai()}"
                    logger.info(f"AI Coach injected summary size: {len(project_state_context)} chars")

                    # Check workflow validation status
                    workflow_val = state.workflow_validation
                    if workflow_val and not workflow_val.get('is_valid', True):
                        errors = workflow_val.get('errors', [])
                        suggestions = workflow_val.get('suggestions', [])
                        project_state_context += "\n\n⚠️ WORKFLOW STATUS FILE ISSUE DETECTED:\n"
                        project_state_context += "The bmm-workflow-status.yaml file is malformed or missing.\n"
                        if errors:
                            project_state_context += f"Errors: {', '.join(errors)}\n"
                        if suggestions:
                            project_state_context += f"Suggestions: {', '.join(suggestions)}\n"
                        project_state_context += "\n**ACTION REQUIRED:** You should proactively inform the user about this issue "
                        project_state_context += "and suggest running /bmad:bmm:workflows:workflow-init to fix it."
            except Exception as e:
                logger.error(f"AI Coach failed to load project state: {e}")
                project_state_context = f"\n\nProject State Error: {str(e)}"

        phase = context.get('phase', context.get('Phase', 'Unknown'))
        epic_id = context.get('epicId', context.get('epic_id', context.get('epic', 'Unknown')))
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

        # Add BMAD sync version info (Story 5.6)
        bmad_sync_info = ""
        if effective_root:
            try:
                from backend.services.bmad_sync import BMADSyncService
                sync_service = BMADSyncService(effective_root)
                sync_status = sync_service.get_status()
                bmad_sync_info = f"\nBMAD Sync Version: {sync_status.get('current_version', 'unknown')}"
                if sync_status.get('last_updated'):
                    from datetime import datetime
                    last_updated = datetime.fromisoformat(sync_status['last_updated'])
                    bmad_sync_info += f" (Last updated: {last_updated.strftime('%Y-%m-%d')})"
            except Exception as e:
                logger.warning(f"Could not load BMAD sync info: {e}")

        # Format validation summary if present (Story 5.3 AC2)
        validation_context = ""
        if validation_summary:
            validation_context = f"\n\n**Story Validation Results:**\n{validation_summary}"

        # Add BMAD documentation if provided
        bmad_docs_context = ""
        if bmad_docs:
            bmad_docs_context = f"\n\n**BMAD METHODOLOGY DOCUMENTATION** (fetched from http://docs.bmad-method.org):\n\n{bmad_docs}\n\n---\n"

        system_prompt = f"""You are the BMAD Coach AI assistant for this BMAD project dashboard.

BMAD Method Documentation: http://docs.bmad-method.org (Version: {bmad_version}){bmad_sync_info}

You help developers working on BMAD projects by providing contextual guidance based on their current project state.

Current Project Context:
- Phase: {phase}
- Epic: {epic_id}{' - ' + epic_title if epic_title else ''}
- Story: {story_id}{' - ' + story_title if story_title else ''}
- Story Status: {story_status}
- Task Progress: {task_progress}
- Current Task: {current_task} [{current_task_status}]{task_list_str}{ac_str}{validation_context}
{project_state_context}
{bmad_docs_context}
**BMAD Dash File Structure Requirements:**

Story files must follow these strict requirements:
1. **Location**: Story files MUST be in `_bmad-output/implementation-artifacts/` directory
   - File naming pattern: `{{epic}}-{{story}}-{{slug}}.md` (e.g., `1-1-living-orb-overlay-core.md`)
   - NOT in subdirectories like `stories/` or `epics/epic-1/`

2. **Format**: Story files must be pure markdown WITHOUT YAML frontmatter
   - NO `---` delimiters at the top of the file
   - NO frontmatter fields like `id:`, `title:`, `epic:`, `status:`
   - Start directly with `# Story X.Y: Title`
   - Example correct format:
     ```
     # Story 1.1: Living Orb & Overlay Core

     ## User Story
     As a User...

     ## Acceptance Criteria
     **Given** ...

     ## Implementation Tasks
     - [ ] Task 1
     - [ ] Task 2
     ```

3. **Metadata Source**: All story metadata comes from `sprint-status.yaml`
   - The `development_status:` section defines story IDs, statuses, and slugs
   - Story files contain only the content (user story, AC, tasks)
   - The backend parser reads metadata from sprint-status.yaml, NOT from story files

4. **Common Issues & Diagnosis**:
   - **Error: "'NoneType' object is not subscriptable"** → Story files have YAML frontmatter (remove it)
   - **Story details empty** → Story file in wrong location (move to `_bmad-output/implementation-artifacts/`)
   - **Project won't load** → Malformed sprint-status.yaml or missing required files

5. **How to Fix Structural Issues**:
   - Check story files are in `_bmad-output/implementation-artifacts/` (NOT in subdirectories)
   - Verify story files have NO YAML frontmatter (should start with `# Story`)
   - Confirm story keys in sprint-status.yaml match filenames (e.g., `1-1-living-orb-overlay-core`)
   - Ensure sprint-status.yaml uses `development_status:` format with proper epic/story entries

When users report issues loading projects or viewing story details, first check these file structure requirements.

CRITICAL - About BMAD Method Documentation:
{"**When asked about BMAD methodology, use the documentation provided above to answer questions.** Explain principles, workflows, and concepts based on the fetched documentation. If the documentation doesn't cover the specific question, acknowledge this and direct users to http://docs.bmad-method.org for more details." if bmad_docs else "**For questions about BMAD methodology, I will fetch and read the official documentation to provide accurate answers.** Do not invent or guess about BMAD principles, workflows, or concepts. Focus on the current project state, evidence gaps, and next steps based on what you know."}

Your Role:
- Provide project-aware answers based on current phase, epic, story, and task
- Suggest appropriate BMAD workflows based on story state (use the workflow commands, don't explain them)
- Help validate AI agent outputs by comparing claims vs. Git/test evidence
- Detect workflow gaps and suggest corrective actions
- For BMAD methodology questions: Direct to http://docs.bmad-method.org

Response Guidelines:
- Be concise and actionable
- Format code blocks with proper syntax highlighting
- When suggesting commands, provide copy-paste ready format
- If you don't know something specific about the project, acknowledge it
- Maintain conversation context across multiple turns

BMAD Workflow Suggestions:
When user asks "What should I do next?", analyze the current story status and suggest:
- If status is "TODO" or "READY_FOR_DEV" → Suggest: `/bmad:bmm:workflows:dev-story {story_id}`
  Explanation: "Start development on this story by running the dev-story workflow."

- If status is "IN_PROGRESS" → Check progress:
  - If tasks incomplete → Suggest: "Continue implementing the remaining tasks"
  - If tasks complete → Suggest: `/bmad:bmm:workflows:code-review {story_id}`
  Explanation: "Run the code-review workflow to validate your implementation."

- If status is "REVIEW" → Suggest: `/bmad:bmm:workflows:code-review {story_id}`
  Explanation: "Run the adversarial code review to find and fix any issues."

- If status is "DONE" or "COMPLETE" → Suggest creating the next story or retrospective
  Explanation: "This story is complete. Consider creating the next story or running a retrospective."

When providing workflow commands, always format them with colons (NOT hyphens):
```
/bmad:bmm:workflows:[workflow-name] [story-id]
```

CRITICAL: Use colons (:) not hyphens (-) in workflow commands!

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

            # Detect if user is asking about BMAD methodology (Story 5.7)
            bmad_docs = None
            if self._detect_bmad_methodology_question(message):
                logger.info("Detected BMAD methodology question - fetching documentation")
                # Story 5.6: Prefer local synced docs
                bmad_docs = self._get_local_bmad_docs()
                if not bmad_docs:
                    logger.info("Local docs not found, falling back to remote fetch")
                    bmad_docs = self._fetch_bmad_docs()
                if bmad_docs:
                    logger.info(f"Injecting BMAD docs into prompt: {len(bmad_docs)} chars")

            system_prompt = self._build_system_prompt(context, bmad_docs=bmad_docs)

            # Inject story details if user is asking about a specific story
            system_prompt = self._inject_story_details(message, system_prompt)

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
            # Detect if user is asking about BMAD methodology (Story 5.7)
            bmad_docs = None
            if self._detect_bmad_methodology_question(message):
                logger.info("Detected BMAD methodology question - searching for context")
                # Story 5.6: Prefer local synced docs
                bmad_docs = self._get_local_bmad_docs()
                if not bmad_docs:
                    logger.info("Local docs not found, falling back to remote fetch")
                    bmad_docs = self._fetch_bmad_docs()
                if bmad_docs:
                    logger.info(f"Injecting BMAD docs into prompt: {len(bmad_docs)} chars")

            system_prompt = self._build_system_prompt(context, bmad_docs=bmad_docs)

            # Inject story details if user is asking about a specific story
            system_prompt = self._inject_story_details(message, system_prompt)

            full_prompt = f"{system_prompt}\n\nUser: {message}"

            response = self.model.generate_content(full_prompt)
            return response.text

        except Exception as e:
            # Handle any errors (google.generativeai may not have APIError class)
            return f"Error: {str(e)}"
