"""
Unit tests for TestDiscoverer service
Tests test file discovery and result parsing functionality
"""
import pytest
import os
import tempfile
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from backend.services.test_discoverer import TestDiscoverer
from backend.models.test_evidence import TestEvidence


class TestTestDiscoverer:
    """Test suite for TestDiscoverer class"""
    
    def test_init(self):
        """Test TestDiscoverer initializes correctly"""
        discoverer = TestDiscoverer("/fake/project")
        assert discoverer.project_path == "/fake/project"
        assert discoverer.manual_entries == {}
    
    def test_extract_story_id_dot_format(self):
        """Test extracting story ID from '1.3' format"""
        discoverer = TestDiscoverer("/fake/project")
        assert discoverer._extract_story_id("1.3") == "1.3"
        assert discoverer._extract_story_id("2.2") == "2.2"
    
    def test_extract_story_id_story_prefix(self):
        """Test extracting story ID from 'story-1.3' format"""
        discoverer = TestDiscoverer("/fake/project")
        assert discoverer._extract_story_id("story-1.3") == "1.3"
        assert discoverer._extract_story_id("Story 2.2") == "2.2"
    
    def test_extract_story_id_dash_format(self):
        """Test extracting story ID from '1-3' format"""
        discoverer = TestDiscoverer("/fake/project")
        assert discoverer._extract_story_id("1-3") == "1.3"
        assert discoverer._extract_story_id("2-2") == "2.2"
    
    def test_extract_story_id_invalid(self):
        """Test extracting story ID from invalid format"""
        discoverer = TestDiscoverer("/fake/project")
        assert discoverer._extract_story_id("invalid") is None
        assert discoverer._extract_story_id("") is None
    
    def test_build_test_file_patterns(self):
        """Test building test file patterns"""
        discoverer = TestDiscoverer("/fake/project")
        patterns = discoverer._build_test_file_patterns("1", "3")
        
        assert "test_story_1_3.py" in patterns
        assert "test_story_1_3_*.py" in patterns
        assert "story-1.3.test.js" in patterns
        assert len(patterns) > 0
    
    def test_discover_tests_for_story_finds_python_files(self, tmp_path):
        """Test discovering Python test files"""
        # Create test directory structure
        tests_dir = tmp_path / "tests"
        tests_dir.mkdir()
        
        # Create matching test file
        test_file = tests_dir / "test_story_1_3.py"
        test_file.write_text("# Test file")
        
        discoverer = TestDiscoverer(str(tmp_path))
        files = discoverer.discover_tests_for_story("1.3")
        
        assert len(files) == 1
        assert str(test_file) in files
    
    def test_discover_tests_for_story_finds_js_files(self, tmp_path):
        """Test discovering JavaScript test files"""
        # Create test directory structure
        tests_dir = tmp_path / "frontend" / "tests"
        tests_dir.mkdir(parents=True)
        
        # Create matching test file
        test_file = tests_dir / "story-1.3.test.js"
        test_file.write_text("// Test file")
        
        discoverer = TestDiscoverer(str(tmp_path))
        files = discoverer.discover_tests_for_story("1.3")
        
        assert len(files) == 1
        assert str(test_file) in files
    
    def test_discover_tests_for_story_no_files(self, tmp_path):
        """Test discovering when no test files exist"""
        discoverer = TestDiscoverer(str(tmp_path))
        files = discoverer.discover_tests_for_story("1.3")
        
        assert len(files) == 0
    
    def test_discover_tests_for_story_invalid_id(self, tmp_path):
        """Test discovering with invalid story ID"""
        discoverer = TestDiscoverer(str(tmp_path))
        files = discoverer.discover_tests_for_story("invalid")
        
        assert len(files) == 0
    
    @patch('subprocess.run')
    def test_parse_pytest_results_success(self, mock_run, tmp_path):
        """Test parsing pytest results successfully"""
        # Mock pytest output
        mock_output = """
        ============================= test session starts ==============================
        tests/test_story_1_3.py::test_example PASSED
        tests/test_story_1_3.py::test_another PASSED
        tests/test_story_1_3.py::test_failing FAILED
        ============================= 2 passed, 1 failed in 0.05s ==============================
        """
        
        mock_run.return_value = Mock(
            stdout=mock_output,
            stderr="",
            returncode=1
        )
        
        test_file = tmp_path / "test_story_1_3.py"
        test_file.write_text("# Test")
        
        discoverer = TestDiscoverer(str(tmp_path))
        results = discoverer.parse_pytest_results(str(test_file))
        
        assert results is not None
        assert results["total_tests"] == 3
        assert results["passing_tests"] == 2
        assert results["failing_tests"] == 1
        assert "test_failing" in str(results["failing_test_names"])
    
    @patch('subprocess.run')
    def test_parse_pytest_results_all_passing(self, mock_run, tmp_path):
        """Test parsing pytest results with all passing"""
        mock_output = """
        ============================= test session starts ==============================
        tests/test_story_1_3.py::test_one PASSED
        tests/test_story_1_3.py::test_two PASSED
        ============================= 2 passed in 0.05s ==============================
        """
        
        mock_run.return_value = Mock(
            stdout=mock_output,
            stderr="",
            returncode=0
        )
        
        test_file = tmp_path / "test_story_1_3.py"
        test_file.write_text("# Test")
        
        discoverer = TestDiscoverer(str(tmp_path))
        results = discoverer.parse_pytest_results(str(test_file))
        
        assert results is not None
        assert results["passing_tests"] == 2
        assert results["failing_tests"] == 0
    
    @patch('subprocess.run')
    def test_parse_pytest_results_timeout(self, mock_run, tmp_path):
        """Test handling pytest timeout"""
        mock_run.side_effect = subprocess.TimeoutExpired("pytest", 30)
        
        test_file = tmp_path / "test_story_1_3.py"
        test_file.write_text("# Test")
        
        discoverer = TestDiscoverer(str(tmp_path))
        results = discoverer.parse_pytest_results(str(test_file))
        
        assert results is None
    
    @patch('subprocess.run')
    def test_parse_pytest_results_not_found(self, mock_run, tmp_path):
        """Test handling pytest not found"""
        mock_run.side_effect = FileNotFoundError()
        
        test_file = tmp_path / "test_story_1_3.py"
        test_file.write_text("# Test")
        
        discoverer = TestDiscoverer(str(tmp_path))
        results = discoverer.parse_pytest_results(str(test_file))
        
        assert results is None
    
    @patch('subprocess.run')
    def test_parse_jest_results_success(self, mock_run, tmp_path):
        """Test parsing jest results successfully"""
        mock_output = """
        PASS tests/story-1.3.test.js
          ✓ test one (5ms)
          ✓ test two (3ms)
          ✕ test failing (2ms)
        
        Tests: 2 passed, 1 failed, 3 total
        """
        
        mock_run.return_value = Mock(
            stdout=mock_output,
            stderr="",
            returncode=1
        )
        
        test_file = tmp_path / "story-1.3.test.js"
        test_file.write_text("// Test")
        
        discoverer = TestDiscoverer(str(tmp_path))
        results = discoverer.parse_jest_results(str(test_file))
        
        assert results is not None
        assert results["total_tests"] == 3
        assert results["passing_tests"] == 2
        assert results["failing_tests"] == 1
    
    @patch('subprocess.run')
    def test_parse_jest_results_not_found(self, mock_run, tmp_path):
        """Test handling jest/npm not found"""
        mock_run.side_effect = FileNotFoundError()
        
        test_file = tmp_path / "story-1.3.test.js"
        test_file.write_text("// Test")
        
        discoverer = TestDiscoverer(str(tmp_path))
        results = discoverer.parse_jest_results(str(test_file))
        
        assert results is None
    
    def test_calculate_status_no_tests(self):
        """Test status calculation with no test files"""
        discoverer = TestDiscoverer("/fake/project")
        evidence = TestEvidence(story_id="1.3", test_files=[])
        
        status, _ = discoverer.calculate_status(evidence)
        assert status == "unknown"
    
    def test_calculate_status_failing_tests(self):
        """Test status calculation with failing tests"""
        discoverer = TestDiscoverer("/fake/project")
        evidence = TestEvidence(
            story_id="1.3",
            test_files=["test.py"],
            pass_count=5,
            fail_count=2,
            last_run_time=datetime.now()
        )
        
        status, _ = discoverer.calculate_status(evidence)
        assert status == "red"
    
    def test_calculate_status_recent_passing(self):
        """Test status calculation with recent passing tests"""
        discoverer = TestDiscoverer("/fake/project")
        evidence = TestEvidence(
            story_id="1.3",
            test_files=["test.py"],
            pass_count=5,
            fail_count=0,
            last_run_time=datetime.now() - timedelta(hours=1)
        )
        
        status, _ = discoverer.calculate_status(evidence)
        assert status == "green"
    
    def test_calculate_status_old_passing(self):
        """Test status calculation with old passing tests"""
        discoverer = TestDiscoverer("/fake/project")
        evidence = TestEvidence(
            story_id="1.3",
            test_files=["test.py"],
            pass_count=5,
            fail_count=0,
            last_run_time=datetime.now() - timedelta(hours=25)
        )
        
        status, _ = discoverer.calculate_status(evidence)
        assert status == "yellow"
    
    def test_calculate_status_no_timestamp(self):
        """Test status calculation with no timestamp"""
        discoverer = TestDiscoverer("/fake/project")
        evidence = TestEvidence(
            story_id="1.3",
            test_files=["test.py"],
            pass_count=5,
            fail_count=0,
            last_run_time=None
        )
        
        status, _ = discoverer.calculate_status(evidence)
        assert status == "green"  # Assume recent if no timestamp
    
    def test_get_test_evidence_for_story_no_files(self, tmp_path):
        """Test getting test evidence when no files found"""
        discoverer = TestDiscoverer(str(tmp_path))
        evidence = discoverer.get_test_evidence_for_story("1.3")
        
        assert evidence.story_id == "1.3"
        assert len(evidence.test_files) == 0
        assert evidence.status == "unknown"
    
    @patch('backend.services.test_discoverer.TestDiscoverer.parse_pytest_results')
    def test_get_test_evidence_for_story_with_files(self, mock_parse, tmp_path):
        """Test getting test evidence with test files"""
        # Create test file
        tests_dir = tmp_path / "tests"
        tests_dir.mkdir()
        test_file = tests_dir / "test_story_1_3.py"
        test_file.write_text("# Test")
        
        # Mock parse results
        mock_parse.return_value = {
            "total_tests": 3,
            "passing_tests": 2,
            "failing_tests": 1,
            "failing_test_names": ["test_failing"],
            "last_run_time": datetime.now()
        }
        
        discoverer = TestDiscoverer(str(tmp_path))
        evidence = discoverer.get_test_evidence_for_story("1.3")
        
        assert evidence.story_id == "1.3"
        assert len(evidence.test_files) == 1
        assert evidence.pass_count == 2
        assert evidence.fail_count == 1
        assert len(evidence.failing_test_names) == 1
    
    def test_set_manual_test_status(self):
        """Test setting manual test status"""
        discoverer = TestDiscoverer("/fake/project")
        discoverer.set_manual_test_status("1.3", pass_count=10, fail_count=2)
        
        assert "1.3" in discoverer.manual_entries
        evidence = discoverer.manual_entries["1.3"]
        assert evidence.pass_count == 10
        assert evidence.fail_count == 2
    
    def test_manual_entry_overrides_discovery(self, tmp_path):
        """Test manual entry overrides auto-discovery"""
        discoverer = TestDiscoverer(str(tmp_path))
        
        # Set manual entry
        discoverer.set_manual_test_status("1.3", pass_count=5, fail_count=0)
        
        # Get evidence - should use manual entry
        evidence = discoverer.get_test_evidence_for_story("1.3")
        
        assert evidence.pass_count == 5
        assert evidence.fail_count == 0
    
    def test_clear_manual_test_status(self):
        """Test clearing manual test status"""
        discoverer = TestDiscoverer("/fake/project")
        discoverer.set_manual_test_status("1.3", pass_count=10, fail_count=2)
        
        assert "1.3" in discoverer.manual_entries
        
        discoverer.clear_manual_test_status("1.3")
        
        assert "1.3" not in discoverer.manual_entries
    
    def test_get_test_evidence_aggregates_multiple_files(self, tmp_path):
        """Test aggregating results from multiple test files"""
        # Create multiple test files
        tests_dir = tmp_path / "tests"
        tests_dir.mkdir()
        
        test_file1 = tests_dir / "test_story_1_3.py"
        test_file1.write_text("# Test 1")
        test_file2 = tests_dir / "test_story_1_3_part2.py"
        test_file2.write_text("# Test 2")
        
        discoverer = TestDiscoverer(str(tmp_path))
        
        # Mock parse results for both files
        with patch.object(discoverer, 'parse_pytest_results') as mock_parse:
            mock_parse.side_effect = [
                {
                    "total_tests": 3,
                    "passing_tests": 2,
                    "failing_tests": 1,
                    "failing_test_names": ["test_fail1"],
                    "last_run_time": datetime.now() - timedelta(hours=1)
                },
                {
                    "total_tests": 2,
                    "passing_tests": 2,
                    "failing_tests": 0,
                    "failing_test_names": [],
                    "last_run_time": datetime.now()
                }
            ]
            
            evidence = discoverer.get_test_evidence_for_story("1.3")
            
            assert len(evidence.test_files) == 2
            assert evidence.pass_count == 4  # 2 + 2
            assert evidence.fail_count == 1  # 1 + 0
            assert len(evidence.failing_test_names) == 1


# Import subprocess for timeout test
import subprocess
import time


class TestTestDiscovererEdgeCases:
    """Edge case tests for TestDiscoverer"""
    
    def test_typescript_file_handling(self, tmp_path):
        """Test that .ts test files are handled correctly"""
        tests_dir = tmp_path / "frontend" / "tests"
        tests_dir.mkdir(parents=True)
        
        # Create test file matching pattern for story 1.3
        test_file = tests_dir / "story-1.3.test.ts"
        test_file.write_text("// TypeScript test")
        
        discoverer = TestDiscoverer(str(tmp_path))
        files = discoverer.discover_tests_for_story("1.3")
        
        # Should find .ts file
        assert len(files) == 1
        assert files[0].endswith('.ts')
        
        # Test that .ts files are parsed with jest
        with patch.object(discoverer, 'parse_jest_results') as mock_parse:
            mock_parse.return_value = {
                "total_tests": 5,
                "passing_tests": 5,
                "failing_tests": 0,
                "failing_test_names": [],
                "last_run_time": datetime.now()
            }
            
            evidence = discoverer.get_test_evidence_for_story("1.3")
            
            # Should call jest parser for .ts files
            assert mock_parse.called
    
    def test_duplicate_test_file_prevention(self, tmp_path):
        """Test that duplicate test file paths are prevented"""
        tests_dir = tmp_path / "tests"
        tests_dir.mkdir()
        
        # Create test file that matches multiple patterns
        test_file = tests_dir / "test_story_1_3.py"
        test_file.write_text("# Test")
        
        discoverer = TestDiscoverer(str(tmp_path))
        files = discoverer.discover_tests_for_story("1.3")
        
        # Should only appear once despite matching multiple patterns
        assert len(files) == len(set(files)), "Duplicate file paths found"
        assert len(files) == 1
    
    def test_calculate_status_with_timezone_aware_datetime(self):
        """Test status calculation with timezone-aware datetime"""
        from datetime import timezone
        
        discoverer = TestDiscoverer("/fake/project")
        
        # Create timezone-aware datetime (recent)
        tz_aware_time = datetime.now(timezone.utc) - timedelta(hours=1)
        
        evidence = TestEvidence(
            story_id="1.3",
            test_files=["test.py"],
            pass_count=5,
            fail_count=0,
            last_run_time=tz_aware_time
        )
        
        status, _ = discoverer.calculate_status(evidence)
        
        # Should handle timezone-aware datetime correctly
        assert status == "green"
    
    def test_calculate_status_with_naive_datetime(self):
        """Test status calculation with naive datetime"""
        discoverer = TestDiscoverer("/fake/project")
        
        # Create naive datetime (recent)
        naive_time = datetime.now() - timedelta(hours=1)
        
        evidence = TestEvidence(
            story_id="1.3",
            test_files=["test.py"],
            pass_count=5,
            fail_count=0,
            last_run_time=naive_time
        )
        
        status, _ = discoverer.calculate_status(evidence)
        
        # Should handle naive datetime correctly
        assert status == "green"
    
    def test_story_2_2_self_validation(self, tmp_path):
        """Test that TestDiscoverer can find tests for story 2.2 (this story)"""
        tests_dir = tmp_path / "tests"
        tests_dir.mkdir()
        
        # Create test file matching pattern for story 2.2
        test_file = tests_dir / "test_story_2_2.py"
        test_file.write_text("# Tests for story 2.2")
        
        discoverer = TestDiscoverer(str(tmp_path))
        files = discoverer.discover_tests_for_story("2.2")
        
        # Should find test file for story 2.2
        assert len(files) == 1
        assert "test_story_2_2" in files[0]


class TestTestDiscovererLogging:
    """Logging verification tests for TestDiscoverer"""
    
    @patch('backend.services.test_discoverer.logger')
    def test_init_logs_info(self, mock_logger):
        """Test that initialization logs INFO message"""
        discoverer = TestDiscoverer("/fake/project")
        
        mock_logger.info.assert_called_once()
        assert "/fake/project" in str(mock_logger.info.call_args)
    
    @patch('backend.services.test_discoverer.logger')
    def test_discover_logs_warning_for_invalid_story_id(self, mock_logger):
        """Test that invalid story ID logs WARNING"""
        discoverer = TestDiscoverer("/fake/project")
        discoverer.discover_tests_for_story("invalid")
        
        mock_logger.warning.assert_called()
        assert "Could not extract story ID" in str(mock_logger.warning.call_args)
    
    @patch('backend.services.test_discoverer.logger')
    def test_discover_logs_info_on_success(self, mock_logger, tmp_path):
        """Test that successful discovery logs INFO"""
        tests_dir = tmp_path / "tests"
        tests_dir.mkdir()
        test_file = tests_dir / "test_story_1_3.py"
        test_file.write_text("# Test")
        
        discoverer = TestDiscoverer(str(tmp_path))
        discoverer.discover_tests_for_story("1.3")
        
        # Should log INFO about files found
        info_calls = [str(call) for call in mock_logger.info.call_args_list]
        assert any("Found" in call and "test files" in call for call in info_calls)
    
    @patch('backend.services.test_discoverer.logger')
    def test_manual_entry_logs_info(self, mock_logger):
        """Test that manual entry logs INFO"""
        discoverer = TestDiscoverer("/fake/project")
        discoverer.set_manual_test_status("1.3", pass_count=5, fail_count=0)
        
        # Should log manual entry
        info_calls = [str(call) for call in mock_logger.info.call_args_list]
        assert any("Manual test status set" in call for call in info_calls)
    
    @patch('backend.services.test_discoverer.logger')
    def test_parse_pytest_logs_warning_on_timeout(self, mock_logger, tmp_path):
        """Test that pytest timeout logs WARNING"""
        test_file = tmp_path / "test.py"
        test_file.write_text("# Test")
        
        discoverer = TestDiscoverer(str(tmp_path))
        
        with patch('subprocess.run', side_effect=subprocess.TimeoutExpired("pytest", 30)):
            result = discoverer.parse_pytest_results(str(test_file))
        
        assert result is None
        mock_logger.warning.assert_called()
        assert "timed out" in str(mock_logger.warning.call_args).lower()


class TestTestDiscovererPerformance:
    """Performance tests for TestDiscoverer"""
    
    def test_discovery_performance_requirement(self, tmp_path):
        """Test that discovery completes in <100ms per story (NFR requirement)"""
        # Create test directory with test file matching story pattern
        tests_dir = tmp_path / "tests"
        tests_dir.mkdir()
        
        # Create matching test file
        test_file = tests_dir / "test_story_1_3.py"
        test_file.write_text("# Test file")
        
        discoverer = TestDiscoverer(str(tmp_path))
        
        # Mock pytest execution to avoid subprocess overhead
        with patch.object(discoverer, 'parse_pytest_results') as mock_parse:
            mock_parse.return_value = {
                "total_tests": 5,
                "passing_tests": 5,
                "failing_tests": 0,
                "failing_test_names": [],
                "last_run_time": datetime.now()
            }
            
            # Measure discovery time
            start_time = time.perf_counter()
            evidence = discoverer.get_test_evidence_for_story("1.3")
            end_time = time.perf_counter()
            
            elapsed_ms = (end_time - start_time) * 1000
            
            # Should complete in <100ms (without subprocess overhead)
            assert elapsed_ms < 100, f"Discovery took {elapsed_ms:.2f}ms, expected <100ms"
            assert evidence.story_id == "1.3"
    
    def test_file_discovery_performance(self, tmp_path):
        """Test that file discovery alone is <50ms for typical project"""
        # Create test directory with 50 test files
        tests_dir = tmp_path / "tests"
        tests_dir.mkdir()
        
        for i in range(50):
            test_file = tests_dir / f"test_example_{i}.py"
            test_file.write_text(f"# Test {i}")
        
        discoverer = TestDiscoverer(str(tmp_path))
        
        # Measure file discovery time
        start_time = time.perf_counter()
        files = discoverer.discover_tests_for_story("1.3")
        end_time = time.perf_counter()
        
        elapsed_ms = (end_time - start_time) * 1000
        
        # Should complete in <50ms for typical project
        assert elapsed_ms < 50, f"File discovery took {elapsed_ms:.2f}ms, expected <50ms"
