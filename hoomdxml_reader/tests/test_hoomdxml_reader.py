"""
Unit and regression test for the hoomdxml_reader package.
"""

# Import package, test suite, and other packages as needed
import sys

import pytest

import hoomdxml_reader


def test_hoomdxml_reader_imported():
    """Sample test, will always pass so long as import statement worked."""
    assert "hoomdxml_reader" in sys.modules
