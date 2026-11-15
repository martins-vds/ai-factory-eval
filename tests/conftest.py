"""Project-wide test isolation (AFS harness, target.shared_test_files).

Every database test restores the rows that migrations seeded, so a test that flushes the database (live-server
and browser tests do) can't leave the next test without its seed data.
"""
import pytest


@pytest.fixture(autouse=True)
def django_db_serialized_rollback():
    return True
