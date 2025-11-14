"""
Demo Mode for Claude-Force

Provides mock responses to allow users to explore the system without an API key.
Perfect for testing, demonstrations, and learning the system.
"""

import time
import random
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import asdict
from claude_force.orchestrator import AgentResult


class DemoOrchestrator:
    """
    Demo orchestrator that simulates agent responses without requiring an API key.

    This class mimics the interface of AgentOrchestrator but returns realistic
    mock responses instead of calling the Claude API.

    Usage:
        demo = DemoOrchestrator(config_path=".claude/claude.json")
        result = demo.run_agent("code-reviewer", task="Review this code")
        print(result.output)  # Displays simulated review
    """

    def __init__(self, config_path: str = ".claude/claude.json"):
        """
        Initialize demo orchestrator with configuration.

        Args:
            config_path: Path to claude.json configuration file
        """
        from claude_force.orchestrator import AgentOrchestrator

        # Load config without API key requirement
        self.config_path = Path(config_path)
        if not self.config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

        import json

        with open(self.config_path, "r") as f:
            self.config = json.load(f)

    def _generate_mock_response(self, agent_name: str, task: str) -> str:
        """
        Generate a realistic mock response based on agent type.

        Args:
            agent_name: Name of the agent
            task: Task description

        Returns:
            Simulated agent response
        """
        # Get agent configuration
        agent_config = self.config["agents"].get(agent_name, {})
        domains = agent_config.get("domains", [])

        # Generate response based on agent domains
        if "code-review" in domains or "review" in agent_name:
            return self._mock_code_review(task)
        elif "test" in domains or "test" in agent_name:
            return self._mock_test_writer(task)
        elif "doc" in domains or "doc" in agent_name:
            return self._mock_documentation(task)
        elif "security" in domains or "security" in agent_name:
            return self._mock_security_review(task)
        elif "api" in domains or "api" in agent_name:
            return self._mock_api_designer(task)
        else:
            return self._mock_generic_response(task)

    def _mock_code_review(self, task: str) -> str:
        """Generate mock code review response."""
        return f"""# Code Review Results

## Overview
I've analyzed the code and found several areas for improvement.

## Issues Found

### 1. Error Handling
**Severity:** Medium
**Location:** Lines 15-23

The current error handling could be more robust. Consider:
- Adding specific exception types instead of bare `except`
- Logging errors for debugging
- Providing user-friendly error messages

**Recommendation:**
```python
try:
    result = process_data(input)
except ValueError as e:
    logger.error(f"Invalid data: {{e}}")
    raise ValueError("Please provide valid input data")
except IOError as e:
    logger.error(f"File error: {{e}}")
    raise IOError("Unable to read input file")
```

### 2. Performance Optimization
**Severity:** Low
**Location:** Lines 45-52

Consider caching repeated calculations to improve performance.

### 3. Code Style
**Severity:** Low

- Add docstrings to functions
- Use type hints for better code clarity
- Follow PEP 8 naming conventions

## Summary
- **Total Issues:** 3
- **Critical:** 0
- **Medium:** 1
- **Low:** 2

The code is functional but would benefit from the suggested improvements.

---
*This is a demo response. Actual analysis would be more detailed.*
"""

    def _mock_test_writer(self, task: str) -> str:
        """Generate mock test writing response."""
        return f"""# Test Suite Generated

## Test File: test_module.py

```python
import unittest
from unittest.mock import patch, Mock
from module import function_to_test


class TestModule(unittest.TestCase):
    \"\"\"Test suite for module functionality.\"\"\"

    def setUp(self):
        \"\"\"Set up test fixtures.\"\"\"
        self.test_data = {{"key": "value"}}

    def test_basic_functionality(self):
        \"\"\"Test basic function behavior.\"\"\"
        result = function_to_test(self.test_data)
        self.assertEqual(result, expected_value)

    def test_edge_case_empty_input(self):
        \"\"\"Test handling of empty input.\"\"\"
        result = function_to_test({{}})
        self.assertIsNone(result)

    def test_error_handling(self):
        \"\"\"Test error handling.\"\"\"
        with self.assertRaises(ValueError):
            function_to_test(None)

    @patch('module.external_api')
    def test_external_dependency(self, mock_api):
        \"\"\"Test integration with external API.\"\"\"
        mock_api.return_value = {{"status": "success"}}
        result = function_to_test(self.test_data)
        self.assertTrue(result['success'])


if __name__ == "__main__":
    unittest.main()
```

## Test Coverage

- **Lines Covered:** 85%
- **Branches Covered:** 78%
- **Functions Tested:** 5/6

## Recommendations

1. Add integration tests for database interactions
2. Test concurrent access scenarios
3. Add performance benchmarks

---
*This is a demo response. Actual tests would be customized to your code.*
"""

    def _mock_documentation(self, task: str) -> str:
        """Generate mock documentation response."""
        return f"""# API Documentation

## Overview

This module provides functionality for data processing and transformation.

## Installation

```bash
pip install your-package
```

## Quick Start

```python
from your_package import DataProcessor

# Initialize processor
processor = DataProcessor(config={{"mode": "fast"}})

# Process data
result = processor.process(input_data)
print(result)
```

## API Reference

### DataProcessor

Main class for data processing operations.

#### Constructor

```python
DataProcessor(config: dict = None)
```

**Parameters:**
- `config` (dict, optional): Configuration options
  - `mode` (str): Processing mode - 'fast' or 'thorough'
  - `cache_size` (int): Cache size in MB

**Example:**
```python
processor = DataProcessor(config={{"mode": "thorough", "cache_size": 100}})
```

#### Methods

##### process(data: Any) -> Result

Process input data and return results.

**Parameters:**
- `data` (Any): Input data to process

**Returns:**
- `Result`: Processed result object

**Raises:**
- `ValueError`: If data is invalid
- `ProcessingError`: If processing fails

**Example:**
```python
result = processor.process(my_data)
if result.success:
    print(result.data)
```

## Best Practices

1. Always validate input data
2. Handle errors gracefully
3. Use caching for large datasets

---
*This is a demo response. Actual documentation would match your codebase.*
"""

    def _mock_security_review(self, task: str) -> str:
        """Generate mock security review response."""
        return f"""# Security Analysis Report

## Executive Summary

Security review completed. Found 2 issues requiring attention.

## Findings

### 1. SQL Injection Vulnerability
**Severity:** HIGH
**Location:** database.py:45

**Issue:**
Direct string concatenation in SQL query construction allows SQL injection.

```python
# Vulnerable code
query = f"SELECT * FROM users WHERE name = '{{user_input}}'"
```

**Fix:**
Use parameterized queries:
```python
# Secure code
query = "SELECT * FROM users WHERE name = %s"
cursor.execute(query, (user_input,))
```

### 2. Hardcoded Credentials
**Severity:** MEDIUM
**Location:** config.py:12

**Issue:**
Database password hardcoded in source file.

**Fix:**
Use environment variables:
```python
import os
DB_PASSWORD = os.getenv('DB_PASSWORD')
```

## Security Checklist

- [x] Input validation
- [ ] SQL injection prevention (needs fix)
- [ ] XSS protection
- [x] CSRF tokens
- [ ] Secure credential storage (needs fix)
- [x] HTTPS enforcement

## Recommendations

1. Fix SQL injection vulnerability immediately
2. Move all credentials to environment variables
3. Add input sanitization middleware
4. Implement rate limiting
5. Enable security headers

---
*This is a demo response. Actual security review would be more comprehensive.*
"""

    def _mock_api_designer(self, task: str) -> str:
        """Generate mock API design response."""
        return f"""# API Design Specification

## Endpoints

### GET /api/v1/resources
Retrieve list of resources.

**Query Parameters:**
- `page` (int): Page number (default: 1)
- `limit` (int): Items per page (default: 20, max: 100)
- `filter` (string): Filter criteria

**Response:**
```json
{{
  "data": [
    {{
      "id": "res_123",
      "name": "Resource Name",
      "created_at": "2024-01-01T00:00:00Z"
    }}
  ],
  "pagination": {{
    "page": 1,
    "total_pages": 5,
    "total_items": 100
  }}
}}
```

### POST /api/v1/resources
Create a new resource.

**Request Body:**
```json
{{
  "name": "New Resource",
  "attributes": {{
    "key": "value"
  }}
}}
```

**Response:**
```json
{{
  "id": "res_124",
  "name": "New Resource",
  "created_at": "2024-01-01T00:00:00Z"
}}
```

### PUT /api/v1/resources/:id
Update existing resource.

### DELETE /api/v1/resources/:id
Delete a resource.

## Error Responses

```json
{{
  "error": {{
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": [
      {{
        "field": "name",
        "issue": "Required field missing"
      }}
    ]
  }}
}}
```

## Rate Limiting

- **Limit:** 1000 requests/hour
- **Header:** `X-RateLimit-Remaining`

---
*This is a demo response. Actual API design would match your requirements.*
"""

    def _mock_generic_response(self, task: str) -> str:
        """Generate generic mock response."""
        return f"""# Task Analysis

## Summary
I've analyzed your request and here's my recommendation.

## Approach

1. **Analysis**: Understanding the requirements
   - Identified key objectives
   - Evaluated constraints
   - Reviewed best practices

2. **Implementation**: Recommended solution
   - Use modular design
   - Follow established patterns
   - Implement error handling

3. **Testing**: Quality assurance
   - Unit tests for components
   - Integration tests for workflows
   - Performance benchmarks

## Recommendations

1. Start with a clear design
2. Implement incrementally
3. Test thoroughly
4. Document as you go

## Next Steps

1. Review this proposal
2. Adjust based on feedback
3. Begin implementation
4. Iterate and improve

---
*This is a demo response. Actual response would be tailored to your specific task.*
"""

    def run_agent(
        self,
        agent_name: str,
        task: str,
        model: str = "claude-3-5-sonnet-20241022",
        max_tokens: int = 4096,
        temperature: float = 1.0,
    ) -> AgentResult:
        """
        Simulate running an agent (demo mode).

        Args:
            agent_name: Name of agent to simulate
            task: Task description
            model: Model name (ignored in demo mode)
            max_tokens: Max tokens (ignored in demo mode)
            temperature: Temperature (ignored in demo mode)

        Returns:
            AgentResult with simulated output
        """
        # Validate agent exists
        if agent_name not in self.config["agents"]:
            raise ValueError(
                f"Agent '{agent_name}' not found. "
                f"Available agents: {', '.join(self.config['agents'].keys())}"
            )

        # Simulate processing time
        time.sleep(random.uniform(0.5, 1.5))

        # Generate mock response
        output = self._generate_mock_response(agent_name, task)

        # Create result with demo metadata
        return AgentResult(
            agent_name=agent_name,
            success=True,
            output=output,
            metadata={
                "demo_mode": True,
                "model": model,
                "simulated_tokens": random.randint(500, 2000),
                "simulated_duration_ms": random.randint(800, 2500),
                "task_preview": task[:100] + ("..." if len(task) > 100 else ""),
            },
            errors=[],
        )

    def run_workflow(
        self, workflow_name: str, task: str, model: str = "claude-3-5-sonnet-20241022"
    ) -> List[AgentResult]:
        """
        Simulate running a workflow (demo mode).

        Args:
            workflow_name: Name of workflow to simulate
            task: Initial task description
            model: Model name (ignored in demo mode)

        Returns:
            List of AgentResults from simulated workflow
        """
        # Validate workflow exists
        if workflow_name not in self.config["workflows"]:
            raise ValueError(
                f"Workflow '{workflow_name}' not found. "
                f"Available workflows: {', '.join(self.config['workflows'].keys())}"
            )

        workflow = self.config["workflows"][workflow_name]
        results = []

        current_task = task
        for agent_name in workflow:
            result = self.run_agent(agent_name, current_task, model=model)
            results.append(result)
            # Use output as input for next agent
            current_task = f"Based on previous output:\n\n{result.output}\n\nOriginal task: {task}"

        return results

    def list_agents(self) -> List[Dict[str, Any]]:
        """List all available agents."""
        from claude_force.orchestrator import AgentOrchestrator

        # Create temporary orchestrator just to use list_agents
        # This doesn't require API key
        agents = []
        for name, config in self.config["agents"].items():
            agents.append(
                {
                    "name": name,
                    "file": config["file"],
                    "priority": config["priority"],
                    "domains": config["domains"],
                }
            )
        return agents

    def list_workflows(self) -> Dict[str, List[str]]:
        """List all available workflows."""
        return self.config.get("workflows", {})

    def get_agent_info(self, agent_name: str) -> Dict[str, Any]:
        """Get detailed information about an agent."""
        if agent_name not in self.config["agents"]:
            raise ValueError(f"Agent '{agent_name}' not found")

        agent_config = self.config["agents"][agent_name]
        return {
            "name": agent_name,
            "file": agent_config["file"],
            "contract": agent_config.get("contract", "unknown"),
            "priority": agent_config["priority"],
            "domains": agent_config["domains"],
            "description": f"Demo agent: {agent_name}",
        }
