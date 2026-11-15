import importlib

import pytest


@pytest.fixture(scope='module')
def restore_seed_loans_after_about_browser_test(django_db_blocker):
    yield
    with django_db_blocker.unblock():
        from django.apps import apps
        from django.db import connection

        apps.get_model('loans', 'Loan').objects.all().delete()
        seed_loans = importlib.import_module('src.loans.migrations.0001_initial').seed_loans
        with connection.schema_editor() as schema_editor:
            seed_loans(apps, schema_editor)
