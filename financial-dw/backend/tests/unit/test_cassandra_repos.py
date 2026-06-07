"""
Tests for Cassandra repository implementations.
These require a running Cassandra instance, so they are marked
as integration tests that can be skipped.
"""
import pytest

# These tests require Cassandra - mark them to skip by default
pytestmark = pytest.mark.skip(reason="Requires running Cassandra instance")
