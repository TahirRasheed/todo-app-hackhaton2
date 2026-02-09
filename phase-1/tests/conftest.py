"""
Pytest configuration and fixtures for Phase I tests.

Provides shared test data and fixtures for all unit and integration tests.
"""

import pytest
from datetime import datetime
from typing import List, Dict


@pytest.fixture
def sample_task_data() -> Dict:
    """Sample task data for unit tests."""
    return {
        "title": "Buy groceries",
        "description": "Milk, eggs, bread",
    }


@pytest.fixture
def sample_task_minimal() -> Dict:
    """Minimal sample task (no description)."""
    return {
        "title": "Pay bills",
        "description": "",
    }


@pytest.fixture
def multiple_tasks_data() -> List[Dict]:
    """Multiple sample tasks for testing."""
    return [
        {"title": "Buy groceries", "description": "Milk, eggs, bread"},
        {"title": "Pay bills", "description": ""},
        {"title": "Write report", "description": "Quarterly report"},
    ]


@pytest.fixture
def invalid_task_data() -> Dict:
    """Invalid task data for testing validation."""
    return {
        "empty_title": "",
        "whitespace_title": "   ",
        "none_title": None,
    }
