"""
BMAD Dash - Test File Discovery Service
Discovers and parses test files related to stories
"""
import re
import os
import subprocess
import logging
from typing import List, Optional, Dict, Tuple
from datetime import datetime, timedelta
from pathlib import Path
from backend.models.test_evidence import TestEvidence


logger = logging.getLogger(__name__)

# Constants
MAX_TEST_AGE_HOURS = 24
TEST_EXECUTION_TIMEOUT = 30  # seconds


class TestDiscoverer:
    """
    Discovers test files for stories and parses their results
    """
    
    def __init__(self, project_path: str):
        self.project_path = project_path
        self.manual_entries: Dict[str, TestEvidence] = {}
        logger.info(f"TestDiscoverer initialized for project: {project_path}")
    
    def discover_tests_for_story(self, story_id: str) -> List[str]:
        """
        Discovers test files related to a story
        
        Args:
            story_id: Story identifier (e.g., "1.3", "story-1.3", "2.2")
            
        Returns:
            List of test file paths matching the story
        """
        # Extract epic.story format (e.g., "1.3" from "story-1.3" or "2.2")
        normalized_id = self._extract_story_id(story_id)
        
        if not normalized_id:
            logger.warning(f"Could not extract story ID from: {story_id}")
            return []
        
        # Parse epic and story numbers
        epic, story = normalized_id.split('.')
        
        # Build file patterns to search for
        patterns = self._build_test_file_patterns(epic, story)
        
        # Search directories
        test_dirs = [
            os.path.join(self.project_path, "tests"),
            os.path.join(self.project_path, "backend", "tests"),
            os.path.join(self.project_path, "frontend", "tests"),
            # Support colocated tests (Vite/React convention: tests next to source files)
            os.path.join(self.project_path, "src"),
        ]
        
        matching_files = []
        
        # Phase 1: Filename-based discovery
        for test_dir in test_dirs:
            if not os.path.exists(test_dir):
                continue
            
            # Search recursively by filename pattern
            for pattern in patterns:
                matches = list(Path(test_dir).rglob(pattern))
                for match in matches:
                    file_path = str(match)
                    if file_path not in matching_files:
                        matching_files.append(file_path)
        
        # Phase 2: Content-based discovery (search for story references inside files)
        # This handles projects where tests are named by module, not by story ID
        content_patterns = [
            # Flexible regex patterns for story ID detection
            r'story_id\s*=\s*["\']' + re.escape(normalized_id) + r'["\']',  # story_id = "2.3" (flexible spaces)
            r'story_id\s*:\s*["\']' + re.escape(normalized_id) + r'["\']',  # story_id: "2.3" (YAML/JSON style)
            r'@story\s+' + re.escape(normalized_id),                         # @story 2.3
            r'Story\s+' + re.escape(normalized_id),                          # Story 2.3 (docstring)
            r'story-' + re.escape(epic) + r'\.' + re.escape(story),          # story-2.3
            r'story_' + re.escape(epic) + r'_' + re.escape(story),           # story_2_3
            r'["\']id["\']\s*:\s*["\']' + re.escape(normalized_id) + r'["\']', # "id": "2.3"
        ]
        
        for test_dir in test_dirs:
            if not os.path.exists(test_dir):
                continue
            
            # Search all test files for content matches
            for test_file in Path(test_dir).rglob("test_*.py"):
                file_path = str(test_file)
                if file_path in matching_files:
                    continue  # Already found by filename
                
                try:
                    content = test_file.read_text(encoding='utf-8', errors='ignore')
                    for pattern in content_patterns:
                        if re.search(pattern, content, re.IGNORECASE):
                            matching_files.append(file_path)
                            logger.debug(f"Content match for story {story_id}: {file_path}")
                            break
                except Exception as e:
                    logger.warning(f"Could not read test file {file_path}: {e}")
            
            # Also check JavaScript/TypeScript test files (including JSX/TSX)
            for ext in ['*.test.js', '*.test.ts', '*.test.jsx', '*.test.tsx', '*.spec.js', '*.spec.ts', '*.spec.jsx', '*.spec.tsx']:
                for test_file in Path(test_dir).rglob(ext):
                    file_path = str(test_file)
                    if file_path in matching_files:
                        continue
                    
                    try:
                        content = test_file.read_text(encoding='utf-8', errors='ignore')
                        for pattern in content_patterns:
                            if re.search(pattern, content, re.IGNORECASE):
                                matching_files.append(file_path)
                                logger.debug(f"Content match for story {story_id}: {file_path}")
                                break
                    except Exception as e:
                        logger.warning(f"Could not read test file {file_path}: {e}")
        
        logger.info(f"Found {len(matching_files)} test files for story {story_id}")
        return matching_files
    
    def _extract_story_id(self, story_id: str) -> Optional[str]:
        """
        Extract epic.story format from various input formats
        
        Args:
            story_id: Input in various formats (e.g., "1.3", "story-1.3", "2-2")
            
        Returns:
            Normalized format like "1.3" or None if invalid
        """
        # Already in epic.story format
        if re.match(r'^\d+\.\d+$', story_id):
            return story_id
        
        # Extract from "story-1.3" or "Story 1.3" or "2-2" format
        match = re.search(r'(\d+)[.\-_\s](\d+)', story_id)
        if match:
            return f"{match.group(1)}.{match.group(2)}"
        
        return None
    
    def _build_test_file_patterns(self, epic: str, story: str) -> List[str]:
        """
        Build file patterns to search for test files
        
        Args:
            epic: Epic number (e.g., "1")
            story: Story number (e.g., "3")
            
        Returns:
            List of glob patterns
        """
        # Support both underscore and dash formats
        patterns = [
            # Python patterns
            f"test_story_{epic}_{story}.py",
            f"test_story_{epic}_{story}_*.py",
            f"test_*story*{epic}*{story}*.py",
            f"test_story-{epic}-{story}.py",
            f"test_story-{epic}-{story}_*.py",
            # JavaScript/TypeScript patterns
            f"story-{epic}.{story}.test.js",
            f"*.story.{epic}.{story}.test.js",
            f"story_{epic}_{story}.test.js",
            f"*.story.{epic}_{story}.test.js",
            f"story-{epic}.{story}.test.ts",
            f"*.story.{epic}.{story}.test.ts",
            f"story_{epic}_{story}.test.ts",
            f"*.story.{epic}_{story}.test.ts",
        ]
        
        return patterns
    
    def parse_pytest_results(self, test_file_path: str) -> Optional[Dict]:
        """
        Parse pytest test results by executing pytest
        
        Args:
            test_file_path: Path to test file
            
        Returns:
            Dict with test results or None if parsing fails
            
        Note:
            Returns dict with keys: total_tests, passing_tests, failing_tests,
            failing_test_names, last_run_time. These are converted to pass_count
            and fail_count when creating TestEvidence instances.
        """
        try:
            # Execute pytest with verbose output
            result = subprocess.run(
                ["pytest", test_file_path, "-v", "--tb=short"],
                capture_output=True,
                text=True,
                timeout=TEST_EXECUTION_TIMEOUT,
                cwd=self.project_path
            )
            
            # Parse stdout for test results
            output = result.stdout + result.stderr
            
            # Look for summary line: "X passed, Y failed in Z.XXs"
            summary_match = re.search(
                r'(\d+)\s+passed.*?(\d+)\s+failed',
                output,
                re.IGNORECASE
            )
            
            if not summary_match:
                # Try alternative format: "X passed in Y.XXs"
                alt_match = re.search(r'(\d+)\s+passed', output, re.IGNORECASE)
                if alt_match:
                    passed = int(alt_match.group(1))
                    failed = 0
                else:
                    logger.warning(f"Could not parse pytest summary for {test_file_path}")
                    return None
            else:
                passed = int(summary_match.group(1))
                failed = int(summary_match.group(2))
            
            # Extract failing test names
            failing_tests = []
            # Match patterns like: "test_file.py::test_name FAILED" or "FAILED test_file.py::test_name"
            failed_patterns = [
                r'([^\s]+::[^\s]+)\s+FAILED',  # test_file.py::test_name FAILED
                r'FAILED\s+([^\s]+::[^\s]+)',  # FAILED test_file.py::test_name
            ]
            for pattern in failed_patterns:
                for match in re.finditer(pattern, output, re.IGNORECASE):
                    failing_tests.append(match.group(1))
            
            # Get file modification time as last_run_time
            last_run_time = datetime.fromtimestamp(os.path.getmtime(test_file_path))
            
            return {
                "total_tests": passed + failed,
                "passing_tests": passed,
                "failing_tests": failed,
                "failing_test_names": failing_tests,
                "last_run_time": last_run_time
            }
            
        except subprocess.TimeoutExpired:
            logger.warning(f"Pytest execution timed out for {test_file_path}")
            return None
        except FileNotFoundError:
            logger.warning(f"Pytest not found - cannot execute tests for {test_file_path}")
            return None
        except Exception as e:
            logger.error(f"Error parsing pytest results for {test_file_path}: {e}")
            return None
    
    def count_tests_static(self, test_file_path: str) -> int:
        """
        Statically count tests in a file using regex to avoid running them.
        Much faster than executing pytest/jest.
        
        Args:
            test_file_path: Path to test file
            
        Returns:
            Number of test functions/cases found
        """
        try:
            with open(test_file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            count = 0
            if test_file_path.endswith('.py'):
                # Count "def test_" functions
                count = len(re.findall(r'^\s*def\s+test_', content, re.MULTILINE))
                # Also count class-based tests if needed (usually handled by def test_ inside class)
            elif any(test_file_path.endswith(ext) for ext in ['.js', '.ts', '.jsx', '.tsx']):
                # Count "it(", "test(", "describe(" blocks? usually just it/test
                count = len(re.findall(r'(?:it|test)\s*\(', content))
                
            return count
        except Exception:
            return 0

    def parse_jest_results(self, test_file_path: str) -> Optional[Dict]:
        """
        Parse jest test results by executing jest
        
        Args:
            test_file_path: Path to test file
            
        Returns:
            Dict with test results or None if parsing fails
            
        Note:
            Returns dict with keys: total_tests, passing_tests, failing_tests,
            failing_test_names, last_run_time. These are converted to pass_count
            and fail_count when creating TestEvidence instances.
        """
        try:
            # Try npm test first, then npx jest
            commands = [
                ["npm", "test", "--", test_file_path],
                ["npx", "jest", test_file_path]
            ]
            
            result = None
            for cmd in commands:
                try:
                    result = subprocess.run(
                        cmd,
                        capture_output=True,
                        text=True,
                        timeout=TEST_EXECUTION_TIMEOUT,
                        cwd=self.project_path
                    )
                    if result.returncode == 0 or "Tests:" in result.stdout:
                        break
                except FileNotFoundError:
                    continue
            
            if not result:
                logger.warning(f"Jest/npm not found - cannot execute tests for {test_file_path}")
                return None
            
            output = result.stdout + result.stderr
            
            # Look for summary: "Tests: X passed, Y failed, Z total"
            summary_match = re.search(
                r'Tests:\s*(\d+)\s+passed.*?(\d+)\s+failed.*?(\d+)\s+total',
                output,
                re.IGNORECASE
            )
            
            if not summary_match:
                # Try alternative format
                alt_match = re.search(r'(\d+)\s+passed.*?(\d+)\s+total', output, re.IGNORECASE)
                if alt_match:
                    passed = int(alt_match.group(1))
                    total = int(alt_match.group(2))
                    failed = total - passed
                else:
                    logger.warning(f"Could not parse jest summary for {test_file_path}")
                    return None
            else:
                passed = int(summary_match.group(1))
                failed = int(summary_match.group(2))
                total = int(summary_match.group(3))
            
            # Extract failing test names
            failing_tests = []
            failed_pattern = r'FAIL\s+([^\s]+)'
            for match in re.finditer(failed_pattern, output):
                failing_tests.append(match.group(1))
            
            # Get file modification time as last_run_time
            # NOTE: Uses file mtime as proxy for test execution time. If test file
            # is edited after tests run, this timestamp may not reflect actual test
            # execution time. This is a known limitation - test frameworks don't
            # provide execution timestamps in their output.
            last_run_time = datetime.fromtimestamp(os.path.getmtime(test_file_path))
            
            return {
                "total_tests": total,
                "passing_tests": passed,
                "failing_tests": failed,
                "failing_test_names": failing_tests,
                "last_run_time": last_run_time
            }
            
        except subprocess.TimeoutExpired:
            logger.warning(f"Jest execution timed out for {test_file_path}")
            return None
        except Exception as e:
            logger.error(f"Error parsing jest results for {test_file_path}: {e}")
            return None
    
    def calculate_status(self, test_evidence: TestEvidence) -> Tuple[str, Optional[datetime]]:
        """
        Calculate status based on test results and recency
        
        Args:
            test_evidence: TestEvidence instance
            
        Returns:
            Tuple of (status, last_run_time)
            Status: "green" (all passing, recent), "yellow" (old), "red" (failing), "unknown" (no tests)
        """
        # If no test files found
        if not test_evidence.test_files:
            return ("unknown", None)
        
        # If no test results (parsing failed)
        if test_evidence.pass_count == 0 and test_evidence.fail_count == 0:
            return ("unknown", test_evidence.last_run_time)
        
        # If any tests failing
        if test_evidence.fail_count > 0:
            return ("red", test_evidence.last_run_time)
        
        # Check recency if last_run_time exists
        if test_evidence.last_run_time:
            # Handle timezone-aware and naive datetimes
            if test_evidence.last_run_time.tzinfo is not None:
                now = datetime.now(test_evidence.last_run_time.tzinfo)
            else:
                now = datetime.now()
            
            age = now - test_evidence.last_run_time
            
            if age > timedelta(hours=MAX_TEST_AGE_HOURS):
                return ("yellow", test_evidence.last_run_time)
            else:
                return ("green", test_evidence.last_run_time)
        
        # All tests passing but no timestamp - assume recent
        return ("green", test_evidence.last_run_time)
    
    def get_test_evidence_for_story(self, story_id: str, project_root: Optional[str] = None) -> TestEvidence:
        """
        Get complete test evidence for a story
        
        Args:
            story_id: Story identifier
            project_root: Optional project root (uses self.project_path if not provided)
            
        Returns:
            TestEvidence instance with all fields populated
        """
        # Check for manual entry first
        if story_id in self.manual_entries:
            logger.info(f"Using manual test status entry for story {story_id}")
            return self.manual_entries[story_id]
        
        project_path = project_root or self.project_path
        
        # Discover test files
        test_files = self.discover_tests_for_story(story_id)
        
        if not test_files:
            logger.info(f"No test files found for story {story_id}")
            return TestEvidence(
                story_id=story_id,
                test_files=[],
                status="unknown"
            )
        
        # Aggregate results across all test files
        total_passing = 0
        total_failing = 0
        all_failing_tests = []
        most_recent_time = None
        
        for test_file in test_files:
            # Determine file type
            if test_file.endswith('.py'):
                results = self.parse_pytest_results(test_file)
            elif test_file.endswith('.js') or test_file.endswith('.ts'):
                results = self.parse_jest_results(test_file)
            else:
                logger.warning(f"Unknown test file type: {test_file}")
                continue
            
            if results:
                total_passing += results["passing_tests"]
                total_failing += results["failing_tests"]
                all_failing_tests.extend(results["failing_test_names"])
                
                # Track most recent execution time
                if results["last_run_time"]:
                    if not most_recent_time or results["last_run_time"] > most_recent_time:
                        most_recent_time = results["last_run_time"]
        
        # Create TestEvidence instance
        test_evidence = TestEvidence(
            story_id=story_id,
            test_files=test_files,
            pass_count=total_passing,
            fail_count=total_failing,
            failing_test_names=all_failing_tests,
            last_run_time=most_recent_time
        )
        
        # Calculate status
        status, _ = self.calculate_status(test_evidence)
        test_evidence.status = status
        
        logger.info(f"Test evidence for story {story_id}: {total_passing} passing, {total_failing} failing")
        return test_evidence
    
    def set_manual_test_status(
        self,
        story_id: str,
        pass_count: int,
        fail_count: int,
        last_run_time: Optional[datetime] = None
    ) -> None:
        """
        Set manual test status entry (NFR23)
        
        Args:
            story_id: Story identifier
            pass_count: Number of passing tests
            fail_count: Number of failing tests
            last_run_time: Optional timestamp of last test run
        """
        test_evidence = TestEvidence(
            story_id=story_id,
            test_files=[],
            pass_count=pass_count,
            fail_count=fail_count,
            failing_test_names=[],
            last_run_time=last_run_time or datetime.now()
        )
        
        # Calculate status
        status, _ = self.calculate_status(test_evidence)
        test_evidence.status = status
        
        self.manual_entries[story_id] = test_evidence
        logger.info(f"Manual test status set for story {story_id}: {pass_count} passing, {fail_count} failing")
    
    def clear_manual_test_status(self, story_id: str) -> None:
        """
        Clear manual test status entry
        
        Args:
            story_id: Story identifier
        """
        if story_id in self.manual_entries:
            del self.manual_entries[story_id]
            logger.info(f"Manual test status cleared for story {story_id}")
