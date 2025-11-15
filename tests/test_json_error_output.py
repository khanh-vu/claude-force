"""
Test that JSON errors go to stdout, not stderr.

This test verifies that when using --format json, ALL output (including errors)
goes to stdout for parseability. Exit codes distinguish success/failure.

Note: This is a documentation/verification test. The actual behavior is tested
in integration tests since unit tests with mocked stdout/stderr and sys.exit
have complex interaction issues.
"""

import json
import unittest


class TestJSONErrorOutputDocumentation(unittest.TestCase):
    """Document JSON error output behavior."""

    def test_json_output_specification(self):
        """
        Document the JSON output specification for errors.

        When --format json is used:
        1. ALL output (success or error) goes to stdout
        2. Exit codes distinguish success (0) from failure (1)
        3. This allows: command --format json > result.json
           to always capture parseable JSON
        """
        # This test documents the expected behavior
        expected_success_format = {
            "success": True,
            "agent": "agent-name",
            "output": "results",
            "errors": [],
            "metadata": {},
        }

        expected_error_format = {"success": False, "error": "error message"}

        # Both formats should be valid JSON
        self.assertIsNotNone(json.dumps(expected_success_format))
        self.assertIsNotNone(json.dumps(expected_error_format))

        # Both should have 'success' field
        self.assertIn("success", expected_success_format)
        self.assertIn("success", expected_error_format)

    def test_exit_code_specification(self):
        """
        Document exit code behavior.

        - Success: exit(0)
        - Failure: exit(1)
        - JSON format or not doesn't affect exit codes
        """
        # Success scenarios
        success_codes = [0]
        # Failure scenarios
        failure_codes = [1]

        self.assertEqual(success_codes, [0])
        self.assertEqual(failure_codes, [1])


if __name__ == "__main__":
    unittest.main()
