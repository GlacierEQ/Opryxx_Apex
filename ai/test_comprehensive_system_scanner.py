"""
Advanced Test Suite for Comprehensive System Scanner

This module provides comprehensive testing for the system scanner including:
- Unit tests for individual components
- Integration tests for component interactions
- Performance benchmarks
- Security validation tests
"""

import asyncio
import hashlib
import json
import logging
import os
import platform
import pytest
import shutil
import tempfile
import time
import unittest
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from unittest.mock import MagicMock, Mock, patch, AsyncMock, call

import psutil

# Import the modules to test
from comprehensive_system_scanner import (
    ComprehensiveSystemScanner,
    DynamicRepairEngine,
    ProtectionEngine,
    SystemIssue,
    RepairAction,
    CommandExecutionError,
    RepairTemplate
)

# Configure test logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_system_scanner.log'),
        logging.StreamHandler()
    ]
)
test_logger = logging.getLogger(__name__)

# Test constants
TEST_DIR = Path(__file__).parent.absolute()
TEST_DATA_DIR = TEST_DIR / 'test_data'
TEST_FILES_DIR = TEST_DATA_DIR / 'test_files'

# Ensure test directories exist
TEST_FILES_DIR.mkdir(parents=True, exist_ok=True)

class TestSystemIssue(unittest.TestCase):
    """Test suite for SystemIssue dataclass functionality.

    Tests cover all aspects of SystemIssue including creation, validation,
    default values, and edge cases.
    """

    def setUp(self) -> None:
        """Set up test fixtures before each test method."""
        self.test_issue = SystemIssue(
            issue_id="TEST001",
            category="performance",
            severity="HIGH",
            description="High CPU usage detected",
            impact="System slowdown",
            auto_fixable=True,
            fix_commands=["taskkill /f /im process.exe"],
            manual_steps=["Check task manager"],
            prevention_measures=["Regular monitoring"]
        )

    def test_system_issue_creation(self) -> None:
        """Test creating a SystemIssue with all fields populated."""
        self.assertEqual(self.test_issue.issue_id, "TEST001")
        self.assertEqual(self.test_issue.category, "performance")
        self.assertEqual(self.test_issue.severity, "HIGH")
        self.assertEqual(self.test_issue.description, "High CPU usage detected")
        self.assertEqual(self.test_issue.impact, "System slowdown")
        self.assertTrue(self.test_issue.auto_fixable)
        self.assertEqual(len(self.test_issue.fix_commands), 1)
        self.assertEqual(len(self.test_issue.manual_steps), 1)
        self.assertEqual(len(self.test_issue.prevention_measures), 1)

    def test_system_issue_defaults(self) -> None:
        """Test SystemIssue with default values."""
        issue = SystemIssue(
            issue_id="TEST002",
            category="security",
            severity="CRITICAL",
            description="Security vulnerability",
            impact="Data breach risk",
            auto_fixable=False
        )

        self.assertEqual(len(issue.fix_commands), 0)
        self.assertEqual(len(issue.manual_steps), 0)
        self.assertEqual(len(issue.prevention_measures), 0)

    def test_system_issue_immutability(self) -> None:
        """Test that SystemIssue instances are immutable."""
        with self.assertRaises(AttributeError):
            self.test_issue.issue_id = "NEW_ID"  # type: ignore

    def test_system_issue_equality(self) -> None:
        """Test equality comparison of SystemIssue instances."""
        same_issue = SystemIssue(
            issue_id="TEST001",  # Same ID as test_issue
            category="performance",
            severity="HIGH",
            description="High CPU usage detected",
            impact="System slowdown",
            auto_fixable=True
        )
        different_issue = SystemIssue(
            issue_id="DIFFERENT",
            category="security",
            severity="LOW",
            description="Different issue",
            impact="Minimal",
            auto_fixable=False
        )

        self.assertEqual(self.test_issue, same_issue)
        self.assertNotEqual(self.test_issue, different_issue)

class TestRepairAction(unittest.TestCase):
    """Test suite for RepairAction dataclass functionality.

    Tests cover all aspects of RepairAction including creation, validation,
    and behavior with different command types.
    """

    def setUp(self) -> None:
        """Set up test fixtures before each test method."""
        self.test_action = RepairAction(
            action_id="REPAIR001",
            name="Test Repair",
            description="Test repair action",
            commands=["echo test", "exit 0"],
            requires_admin=False,
            estimated_time=60,
            success_criteria=["test completed", "success"],
            rollback_commands=["echo rollback"]
        )

    def test_repair_action_creation(self) -> None:
        """Test creating a RepairAction with all fields populated."""
        self.assertEqual(self.test_action.action_id, "REPAIR001")
        self.assertEqual(self.test_action.name, "Test Repair")
        self.assertEqual(self.test_action.description, "Test repair action")
        self.assertEqual(len(self.test_action.commands), 2)
        self.assertFalse(self.test_action.requires_admin)
        self.assertEqual(self.test_action.estimated_time, 60)
        self.assertEqual(len(self.test_action.success_criteria), 2)
        self.assertEqual(len(self.test_action.rollback_commands), 1)

    def test_repair_action_defaults(self) -> None:
        """Test RepairAction with minimal required fields."""
        action = RepairAction(
            action_id="MINIMAL",
            name="Minimal Action",
            description="Minimal action description",
            commands=[],
            requires_admin=False,
            estimated_time=0,
            success_criteria=[]
        )

        self.assertEqual(action.action_id, "MINIMAL")
        self.assertEqual(action.name, "Minimal Action")
        self.assertEqual(len(action.commands), 0)
        self.assertEqual(len(action.success_criteria), 0)
        self.assertEqual(len(action.rollback_commands), 0)

    def test_repair_action_immutability(self) -> None:
        """Test that RepairAction instances are immutable."""
        with self.assertRaises(AttributeError):
            self.test_action.action_id = "NEW_ID"  # type: ignore

    def test_repair_action_equality(self) -> None:
        """Test equality comparison of RepairAction instances."""
        same_action = RepairAction(
            action_id="REPAIR001",  # Same ID as test_action
            name="Test Repair",
            description="Test repair action",
            commands=["echo test", "exit 0"],
            requires_admin=False,
            estimated_time=60,
            success_criteria=["test completed", "success"],
            rollback_commands=["echo rollback"]
        )
        different_action = RepairAction(
            action_id="DIFFERENT",
            name="Different Action",
            description="Different description",
            commands=["echo different"],
            requires_admin=True,
            estimated_time=120,
            success_criteria=["different"],
            rollback_commands=[]
        )

        self.assertEqual(self.test_action, same_action)
        self.assertNotEqual(self.test_action, different_action)

    def test_repair_action_str_representation(self) -> None:
        """Test the string representation of RepairAction."""
        action_str = str(self.test_action)
        self.assertIn("REPAIR001", action_str)
        self.assertIn("Test Repair", action_str)
        self.assertIn("Test repair action", action_str)

class TestDynamicRepairEngine(unittest.IsolatedAsyncioTestCase):
    """Advanced tests for DynamicRepairEngine

    This test suite verifies the functionality of the DynamicRepairEngine class,
    including repair execution, template management, and error handling.
    """

    def setUp(self) -> None:
        """Set up test environment before each test method."""
        self.repair_engine = DynamicRepairEngine()
        self.test_repair_action = RepairAction(
            action_id="test_repair",
            name="Test Repair Action",
            description="A test repair action",
            commands=["echo 'test command'"],
            requires_admin=False,
            estimated_time=30,
            success_criteria=["test command"],
            rollback_commands=["echo 'rollback command'"]
        )

        # Create a test directory for file operations
        self.test_dir = TEST_FILES_DIR / f"test_repair_{int(time.time())}"
        self.test_dir.mkdir(exist_ok=True)

        # Create a test file for file-based tests
        self.test_file = self.test_dir / "test_file.txt"
        self.test_file.write_text("Test content")

    def tearDown(self) -> None:
        """Clean up after each test method."""
        # Clean up test directory
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_initialization(self) -> None:
        """Test that the repair engine initializes correctly."""
        self.assertIsNotNone(self.repair_engine.repair_queue)
        self.assertIsInstance(self.repair_engine.repair_queue, asyncio.Queue)
        self.assertEqual(len(self.repair_engine.active_repairs), 0)
        self.assertEqual(len(self.repair_engine.repair_history), 0)
        self.assertEqual(len(self.repair_engine.protection_monitors), 0)

    def test_repair_templates_initialization(self) -> None:
        """Test that repair templates are properly initialized."""
        templates = self.repair_engine.repair_templates

        # Check that required templates exist
        required_templates = [
            "temp_cleanup",
            "service_optimization",
            "startup_optimization",
            "disk_cleanup",
            "registry_cleanup"
        ]

        for template_name in required_templates:
            with self.subTest(template=template_name):
                self.assertIn(template_name, templates)
                template = templates[template_name]
                self.assertIsInstance(template, RepairAction)
                self.assertIsInstance(template.name, str)
                self.assertIsInstance(template.description, str)
                self.assertIsInstance(template.commands, list)
                self.assertIsInstance(template.requires_admin, bool)
                self.assertIsInstance(template.estimated_time, int)
                self.assertIsInstance(template.success_criteria, list)
                self.assertIsInstance(template.rollback_commands, list)

    @patch('subprocess.run')
    async def test_execute_command_success(self, mock_subprocess: Mock) -> None:
        """Test successful command execution."""
        # Mock successful subprocess result
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "Command executed successfully"
        mock_result.stderr = ""
        mock_subprocess.return_value = mock_result

        result = await self.repair_engine._execute_command("echo test", False)

        # Verify command execution
        self.assertTrue(result["success"])
        self.assertEqual(result["return_code"], 0)
        self.assertIn("Command executed successfully", result["stdout"])
        self.assertEqual(result["stderr"], "")

        # Verify subprocess was called correctly
        mock_subprocess.assert_called_once()
        call_args = mock_subprocess.call_args[0][0]
        self.assertIn("echo test", " ".join(call_args))

    @patch('subprocess.run')
    async def test_execute_command_with_admin_privileges(self, mock_subprocess: Mock) -> None:
        """Test command execution that requires admin privileges."""
        # Mock successful subprocess result
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "Admin command executed"
        mock_result.stderr = ""
        mock_subprocess.return_value = mock_result

        # Skip actual admin check in tests
        with patch('comprehensive_system_scanner.is_admin', return_value=True):
            result = await self.repair_engine._execute_command("admin_command", True)

        self.assertTrue(result["success"])
        self.assertEqual(result["return_code"], 0)

        # On Windows, should use 'runas' for admin commands
        if platform.system() == "Windows":
            call_args = mock_subprocess.call_args[0][0]
            self.assertIn("runas", " ".join(call_args).lower())

    @patch('subprocess.run')
    async def test_execute_command_failure(self, mock_subprocess: Mock) -> None:
        """Test failed command execution."""
        # Mock failed subprocess result
        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "Command failed: No such file or directory"
        mock_subprocess.return_value = mock_result

        # Test with a command that will fail
        result = await self.repair_engine._execute_command("invalid_command", False)

        self.assertFalse(result["success"])
        self.assertEqual(result["return_code"], 1)
        self.assertIn("No such file or directory", result["stderr"])

    @patch('subprocess.run')
    async def test_execute_repair_success(self, mock_subprocess: Mock) -> None:
        """Test successful repair execution with progress callbacks."""
        # Setup mock for command execution
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "test command executed successfully"
        mock_result.stderr = ""
        mock_subprocess.return_value = mock_result

        # Create a mock progress callback
        progress_callback = Mock()

        # Execute the repair
        result = await self.repair_engine.execute_repair(
            self.test_repair_action,
            progress_callback=progress_callback
        )

        # Verify the result
        self.assertTrue(result["success"])
        self.assertIn("repair_id", result)
        self.assertIn("duration", result)
        self.assertGreater(result["duration"], 0)

        # Verify progress callback was called with expected arguments
        progress_callback.assert_called()
        call_args = progress_callback.call_args_list

        # Should have at least one progress update
        self.assertGreaterEqual(len(call_args), 1)

        # First call should be starting the repair
        self.assertIn("Starting", call_args[0][0][0])
        self.assertEqual(call_args[0][0][1], 0)  # 0% progress

        # Last call should be completion
        self.assertIn("completed", call_args[-1][0][0].lower())
        self.assertEqual(call_args[-1][0][1], 100)  # 100% progress

    def test_check_success_criteria_with_criteria(self) -> None:
        """Test success criteria checking with specific criteria."""
        test_cases = [
            # Test case 1: All criteria matched
            (
                [
                    {"stdout": "Operation completed successfully", "stderr": "", "success": True},
                    {"stdout": "All tests passed", "stderr": "", "success": True}
                ],
                ["completed successfully", "tests passed"],
                True
            ),
            # Test case 2: Some criteria not matched
            (
                [
                    {"stdout": "Operation started", "stderr": "", "success": True},
                    {"stdout": "All tests passed", "stderr": "", "success": True}
                ],
                ["completed successfully", "tests passed"],
                False
            ),
            # Test case 3: Empty results
            (
                [],
                ["some criteria"],
                False
            )
        ]

        for i, (results, criteria, expected) in enumerate(test_cases, 1):
            with self.subTest(test_case=f"test_case_{i}"):
                success = self.repair_engine._check_success_criteria(results, criteria)
                self.assertEqual(success, expected,
                               f"Test case {i} failed: expected {expected} for {results}")

    def test_check_success_criteria_without_criteria(self) -> None:
        """Test success criteria checking without specific criteria."""
        test_cases = [
            # All successful
            (
                [
                    {"success": True},
                    {"success": True}
                ],
                True
            ),
            # Some failures
            (
                [
                    {"success": True},
                    {"success": False}
                ],
                False
            ),
            # Empty results
            (
                [],
                True  # Empty results with no criteria should be considered successful
            )
        ]

        for i, (results, expected) in enumerate(test_cases, 1):
                success = self.repair_engine._check_success_criteria(results, [])
                self.assertEqual(success, expected,
                               f"Test case {i} failed: expected {expected} for {results}")

    def test_check_success_criteria_failure(self) -> None:
        """Test success criteria checking with failure scenarios."""
        test_cases = [
            # Test case 1: One command failed
            (
                [
                    {"stdout": "Operation failed", "stderr": "Error occurred", "success": False},
                    {"stdout": "All tests passed", "stderr": "", "success": True}
                ],
                ["completed successfully", "tests passed"],
                False
            ),
            # Test case 2: All commands failed
            (
                [
                    {"stdout": "Operation failed", "stderr": "Error 1", "success": False},
                    {"stdout": "Test failed", "stderr": "Error 2", "success": False}
                ],
                [],
                False
            )
        ]

        for i, (results, criteria, expected) in enumerate(test_cases, 1):
            with self.subTest(test_case=f"failure_case_{i}"):
                success = self.repair_engine._check_success_criteria(results, criteria)
                self.assertEqual(success, expected,
                              f"Test case {i} failed: expected {expected} for {results}")

    @patch('subprocess.run')
    async def test_execute_repair_with_rollback(self, mock_subprocess: Mock) -> None:
        """Test repair execution with rollback on failure."""
        # First command succeeds, second fails, triggering rollback
        mock_results = [
            Mock(returncode=0, stdout="Step 1 completed", stderr=""),
            Mock(returncode=1, stdout="", stderr="Step 2 failed"),
            Mock(returncode=0, stdout="Rollback executed", stderr="")  # Rollback command
        ]
        mock_subprocess.side_effect = mock_results

        # Create a repair action with rollback commands
        repair_action = RepairAction(
            action_id="test_rollback",
            name="Test Rollback",
            description="Test repair with rollback",
            commands=["step1", "step2_fails"],
            requires_admin=False,
            estimated_time=30,
            success_criteria=["completed"],
            rollback_commands=["rollback_step"]
        )

        # Execute the repair
        result = await self.repair_engine.execute_repair(repair_action)

        # Verify the result
        self.assertFalse(result["success"])
        self.assertIn("rollback", result)
        self.assertTrue(result["rollback"]["executed"])
        self.assertTrue(result["rollback"]["success"])

        # Verify all commands were executed in the right order
        self.assertEqual(mock_subprocess.call_count, 3)

        # Verify rollback command was called with the right arguments
        rollback_call = mock_subprocess.call_args_list[-1]
        self.assertIn("rollback_step", " ".join(rollback_call[0][0]))

    @patch('subprocess.run')
    async def test_rollback_functionality(self, mock_subprocess):
        """Test repair rollback functionality"""
        # Create repair action with rollback commands
        repair_action = RepairAction(
            action_id="rollback_test",
            name="Rollback Test",
            description="Test rollback functionality",
            commands=["failing_command"],
            requires_admin=False,
            estimated_time=30,
            success_criteria=["success"],
            rollback_commands=["echo 'rolling back'"]
        )

        # Mock failing command followed by successful rollback
        mock_results = [
            Mock(returncode=1, stdout="", stderr="Command failed"),  # Failing command
            Mock(returncode=0, stdout="rolling back", stderr="")     # Successful rollback
        ]
        mock_subprocess.side_effect = mock_results

        repair_id = "rollback_test_123"

        # This should trigger rollback due to command failure
        with self.assertRaises(Exception):
            await self.repair_engine._execute_repair_action(
                repair_action, None, repair_id
            )

class TestProtectionEngine(unittest.TestCase):
    """Advanced tests for ProtectionEngine

    This test suite verifies the functionality of the ProtectionEngine class,
    including file integrity monitoring, registry protection, and threat detection.
    """

    def setUp(self) -> None:
        """Set up test environment before each test method."""
        # Prevent actual thread creation during tests
        with patch('threading.Thread'):
            self.protection_engine = ProtectionEngine()

        # Create a test directory for file operations
        self.test_dir = TEST_FILES_DIR / f"test_protection_{int(time.time())}"
        self.test_dir.mkdir(exist_ok=True)

        # Create a test file for file monitoring tests
        self.test_file = self.test_dir / "test_file.txt"
        self.test_file.write_text("Test content")

        # Store original methods for restoration in tearDown
        self.original_methods = {
            '_monitor_file_integrity': self.protection_engine._monitor_file_integrity,
            '_monitor_registry': self.protection_engine._monitor_registry,
            '_scan_for_threats': self.protection_engine._scan_for_threats
        }

    def tearDown(self) -> None:
        """Clean up after each test method."""
        # Clean up test directory
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir, ignore_errors=True)

        # Restore original methods
        for name, method in self.original_methods.items():
            setattr(self.protection_engine, name, method)

    def test_initialization(self) -> None:
        """Test that the protection engine initializes correctly."""
        self.assertIsInstance(self.protection_engine.protection_rules, dict)
        self.assertIsInstance(self.protection_engine.threat_database, dict)
        self.assertIsInstance(self.protection_engine.file_hashes, dict)
        self.assertIsInstance(self.protection_engine.running, bool)

    def test_protection_rules_initialization(self) -> None:
        """Test that protection rules are properly initialized."""
        rules = self.protection_engine.protection_rules

        # Check that required rule categories exist
        required_categories = [
            "file_integrity",
            "registry_protection",
            "process_monitoring",
            "network_protection"
        ]

        for category in required_categories:
            with self.subTest(category=category):
                self.assertIn(category, rules)
                self.assertIsInstance(rules[category], dict)

        # Check file integrity rules in detail
        file_rules = rules["file_integrity"]
        self.assertIn("monitor_paths", file_rules)
        self.assertIn("check_interval", file_rules)
        self.assertIn("alert_on_change", file_rules)
        self.assertIsInstance(file_rules["monitor_paths"], list)
        self.assertIsInstance(file_rules["check_interval"], (int, float))
        self.assertIsInstance(file_rules["alert_on_change"], bool)

    @patch('os.path.exists')
    @patch('builtins.open')
    def test_threat_database_loading(self, mock_open: Mock, mock_exists: Mock) -> None:
        """Test loading threat database from file."""
        # Mock the threat database file
        mock_exists.return_value = True
        mock_file_content = {
            "malicious_hashes": ["abc123", "def456"],
            "suspicious_domains": ["malware.com", "phishing-site.com"],
            "known_threats": [
                {
                    "name": "TestMalware",
                    "type": "trojan",
                    "signatures": ["evil_pattern"],
                    "mitre_techniques": ["T1059"]
                }
            ],
            "last_updated": "2023-01-01T00:00:00"
        }
        mock_open.return_value.__enter__.return_value.read.return_value = json.dumps(mock_file_content)

        # Create a new instance to trigger database loading
        with patch('threading.Thread'):
            engine = ProtectionEngine()

        # Verify the threat database was loaded correctly
        self.assertEqual(engine.threat_database["malicious_hashes"], ["abc123", "def456"])
        self.assertEqual(engine.threat_database["suspicious_domains"], ["malware.com", "phishing-site.com"])
        self.assertEqual(len(engine.threat_database["known_threats"]), 1)
        self.assertEqual(engine.threat_database["known_threats"][0]["name"], "TestMalware")

    def test_file_hash_calculation(self) -> None:
        """Test file hash calculation with known content."""
        # Create a file with known content
        test_content = "This is a test file for hash calculation"
        test_file = self.test_dir / "hash_test.txt"
        test_file.write_text(test_content)

        # Calculate the expected SHA-256 hash
        import hashlib
        expected_hash = hashlib.sha256(test_content.encode('utf-8')).hexdigest()

        # Calculate the actual hash using the protection engine
        actual_hash = self.protection_engine._calculate_file_hash(str(test_file))

        # Verify the hash is correct
        self.assertEqual(actual_hash, expected_hash)
        self.assertEqual(len(actual_hash), 64)  # SHA-256 produces 64-character hashes

    def test_file_hash_calculation_nonexistent_file(self) -> None:
        """Test file hash calculation for non-existent file."""
        non_existent_file = self.test_dir / "nonexistent_file.txt"
        file_hash = self.protection_engine._calculate_file_hash(str(non_existent_file))
        self.assertIsNone(file_hash)

    @patch('os.path.getmtime')
    @patch('os.path.getsize')
    def test_detect_file_changes(self, mock_getsize: Mock, mock_getmtime: Mock) -> None:
        """Test detection of file changes based on size and modification time."""
        # Set up mocks
        test_file = str(self.test_file)
        initial_mtime = 1000.0
        initial_size = 100

        mock_getmtime.return_value = initial_mtime
        mock_getsize.return_value = initial_size

        # First check - should record the baseline
        self.protection_engine._check_file_integrity(test_file)
        self.assertIn(test_file, self.protection_engine.file_hashes)

        # Change file size
        mock_getsize.return_value = 200
        changes = self.protection_engine._check_file_integrity(test_file)
        self.assertTrue(changes["size_changed"])
        self.assertEqual(changes["old_size"], initial_size)
        self.assertEqual(changes["new_size"], 200)

        # Change modification time
        mock_getmtime.return_value = 2000.0
        changes = self.protection_engine._check_file_integrity(test_file)
        self.assertTrue(changes["modified"])
        self.assertEqual(changes["old_mtime"], initial_mtime)
        self.assertEqual(changes["new_mtime"], 2000.0)

    @patch('comprehensive_system_scanner.ProtectionEngine._check_file_integrity')
    def test_monitor_file_integrity(self, mock_check: Mock) -> None:
        """Test file integrity monitoring loop."""
        # Set up test data
        test_file = str(self.test_file)
        self.protection_engine.protection_rules["file_integrity"]["monitor_paths"] = [test_file]

        # Mock the check to report changes on the first call, then stop the loop
        mock_check.side_effect = [
            {"modified": True, "size_changed": False, "hash_changed": False},
            {"modified": False, "size_changed": False, "hash_changed": False}
        ]

        # Mock the running flag to stop after one iteration
        def stop_after_first_iter():
            self.protection_engine.running = False
            return False

        with patch('time.sleep', side_effect=stop_after_first_iter):
            with patch('threading.Thread'):
                self.protection_engine.start_monitoring()

        # Verify the check was called with the test file
        mock_check.assert_called_with(test_file)

    @patch('winreg.OpenKey')
    @patch('winreg.QueryInfoKey')
    @patch('winreg.EnumValue')
    def test_monitor_registry(self, mock_enum_value: Mock, mock_query_info: Mock,
                            mock_open_key: Mock) -> None:
        """Test registry monitoring functionality."""
        # Skip this test on non-Windows platforms
        if platform.system() != 'Windows':
            self.skipTest("Registry tests only run on Windows")

        # Set up test data
        test_key = "SOFTWARE\\TestKey"
        self.protection_engine.protection_rules["registry_protection"]["monitor_keys"] = [test_key]

        # Mock registry operations
        mock_hkey = Mock()
        mock_open_key.return_value.__enter__.return_value = mock_hkey
        mock_query_info.return_value = (1, 1, 0)  # 1 value, 1 subkey, 0 for last modified
        mock_enum_value.return_value = ("TestValue", "test_data", 1)  # name, data, type

        # Call the method directly (not starting a thread)
        self.protection_engine._monitor_registry()

        # Verify the registry key was opened and checked
        mock_open_key.assert_called()
        mock_query_info.assert_called()
        mock_enum_value.assert_called()

    @patch('comprehensive_system_scanner.ProtectionEngine._scan_file_for_threats')
    def test_scan_for_threats(self, mock_scan_file: Mock) -> None:
        """Test threat scanning functionality."""
        # Set up test data
        test_file = str(self.test_file)
        self.protection_engine.protection_rules["file_integrity"]["monitor_paths"] = [self.test_dir]

        # Mock the file scanner to find a threat
        mock_scan_file.return_value = {
            "infected": True,
            "threat_name": "TestMalware",
            "file": test_file
        }

        # Run the scan
        threats = self.protection_engine._scan_for_threats()

        # Verify the threat was detected
        self.assertEqual(len(threats), 1)
        self.assertEqual(threats[0]["threat_name"], "TestMalware")
        self.assertEqual(threats[0]["file"], test_file)

        # Verify the scan_file method was called with the test file
        mock_scan_file.assert_called_with(test_file)
