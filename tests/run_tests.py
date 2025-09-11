#!/usr/bin/env python3
"""
Test runner for South Park episode generator tests.

Usage:
    python run_tests.py                    # Run all tests
    python run_tests.py test_news_research # Run specific test file
    python run_tests.py -m unit           # Run only unit tests
    python run_tests.py -k "test_search"  # Run tests matching pattern
"""

import sys
import pytest

if __name__ == "__main__":
    # Default to running all tests in verbose mode
    args = sys.argv[1:] if len(sys.argv) > 1 else ["-v"]
    
    # Add the tests directory to the args if not already specified
    if not any(arg.startswith("test") for arg in args) and "-m" not in args and "-k" not in args:
        args = ["tests/"] + args
    
    exit_code = pytest.main(args)
    sys.exit(exit_code)