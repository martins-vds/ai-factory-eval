import csv
import json
from datetime import date
from io import StringIO
from pathlib import Path

import pytest
from django.core.exceptions import ValidationError

from src.loans.domain import Loan
from src.loans.models import LoanRecord
from src.loans.repositories import DjangoLoanRepository
from src.loans.services import LoanCatalog, LoanNotFound


@pytest.mark.django_db
def test_catalog_api_matches_characterized_source_responses(client):
    root = Path(__file__).resolve().parents[2]
    source_cases = [
        (root / '.migration/characterization/source/goldens/http.json', 'GET /loans'),
        (root / '.migration/characterization/source/goldens/http.json', 'GET /loans/{id}'),
        (root / '.migration/characterization/source/goldens/edge-cases.json', 'GET /loans/unknown'),
    ]

    for golden_path, case_name in source_cases:
        expected = json.loads(golden_path.read_text())[case_name]
        response = client.get(expected['request']['path'])
        observed = {
            'body': response.content.decode(),
            'content_type': response['Content-Type'].split(';')[0],
            'status': response.status_code,
        }

        assert observed == expected['response']


@pytest.mark.django_db
def test_api_lists_seeded_loans_in_id_order(client):
    response = client.get('/loans')

    assert response.status_code == 200
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == (
        'L1;ana;9780134685991;2026-01-02;2026-01-16;\n'
        'L2;bo;9780596007126;2026-01-10;2026-01-24;2026-01-20\n'
        'L3;cy;9781617294945;2025-12-01;2025-12-15;2026-01-03\n'
    )


@pytest.mark.django_db
def test_api_returns_a_loan_line_or_the_characterized_not_found_response(client):
    found = client.get('/loans/L1')
    missing = client.get('/loans/unknown')

    assert found.status_code == 200
    assert found['Content-Type'] == 'text/plain'
    assert found.content.decode() == 'L1;ana;9780134685991;2026-01-02;2026-01-16;\n'
    assert missing.status_code == 404
    assert missing['Content-Type'] == 'text/plain'
    assert missing.content.decode() == 'no such loan\n'


def test_due_date_is_fourteen_calendar_days_after_lending():
    loan = Loan('L1', 'ana', '9780134685991', date(2026, 1, 2), None)

    assert loan.due_on == date(2026, 1, 16)


@pytest.mark.django_db
def test_catalog_use_case_refuses_an_unknown_loan_without_a_request():
    catalog = LoanCatalog(DjangoLoanRepository())

    with pytest.raises(LoanNotFound):
        catalog.get_loan('unknown')


@pytest.mark.django_db
def test_catalog_use_case_lists_seed_records_in_id_order():
    catalog = LoanCatalog(DjangoLoanRepository())

    assert [loan.id for loan in catalog.list_loans()] == ['L1', 'L2', 'L3']


@pytest.mark.django_db
def test_catalog_use_case_orders_records_inserted_out_of_sequence():
    LoanRecord.objects.create(
        id='L9',
        member='reader',
        isbn='9780000000009',
        lent_on=date(2026, 1, 1),
    )
    LoanRecord.objects.create(
        id='L4',
        member='reader',
        isbn='9780000000004',
        lent_on=date(2026, 1, 1),
    )

    loan_ids = [loan.id for loan in LoanCatalog(DjangoLoanRepository()).list_loans()]

    assert loan_ids == ['L1', 'L2', 'L3', 'L4', 'L9']


@pytest.mark.django_db(transaction=True)
def test_catalog_queries_leave_no_transaction_open():
    from django.db import connection

    catalog = LoanCatalog(DjangoLoanRepository())

    catalog.list_loans()
    catalog.get_loan('L1')

    assert not connection.in_atomic_block


@pytest.mark.django_db
def test_active_loan_can_have_no_return_date():
    loan = LoanRecord(
        id='L4',
        member='reader',
        isbn='9780000000000',
        lent_on=date(2026, 1, 1),
        returned_on=None,
    )

    loan.full_clean()


@pytest.mark.django_db
@pytest.mark.parametrize(
    ('field', 'value'),
    [
        ('id', f'L{"0" * 255}'),
        ('member', 'x' * 256),
        ('isbn', 'x' * 256),
    ],
)
def test_loan_text_fields_keep_the_legacy_column_length(field, value):
    fields = {
        'id': 'L4',
        'member': 'reader',
        'isbn': '9780000000000',
        'lent_on': date(2026, 1, 1),
    }
    fields[field] = value
    loan = LoanRecord(**fields)

    with pytest.raises(ValidationError):
        loan.full_clean()


@pytest.mark.django_db
def test_text_export_escapes_semicolons_and_line_breaks():
    LoanRecord.objects.create(
        id='L4',
        member='a;b',
        isbn='123\n456',
        lent_on=date(2026, 1, 1),
    )
    catalog = LoanCatalog(DjangoLoanRepository())
    exported = catalog.text_export()

    rows = list(csv.reader(StringIO(exported), delimiter=';'))
    assert exported.endswith('\n')
    assert rows[-1] == ['L4', 'a;b', '123\n456', '2026-01-01', '2026-01-15', '']


@pytest.mark.django_db(transaction=True)
def test_loan_records_survive_a_database_connection_restart():
    from django.db import connection

    LoanRecord.objects.create(
        id='L4',
        member='reader',
        isbn='9780000000000',
        lent_on=date(2026, 1, 1),
    )

    connection.close()

    assert LoanCatalog(DjangoLoanRepository()).get_loan('L4').member == 'reader'


@pytest.mark.django_db(transaction=True)
def test_reapplying_migrations_does_not_overwrite_persisted_loans():
    from django.core.management import call_command

    LoanRecord.objects.filter(pk='L1').update(member='reader')

    call_command('migrate', 'loans', interactive=False, verbosity=0)

    assert LoanRecord.objects.get(pk='L1').member == 'reader'


@pytest.mark.django_db
def test_unknown_browser_loan_renders_a_not_found_page(client):
    response = client.get('/ui/loans/unknown/')

    assert response.status_code == 404
    assert b'This record is not in the collection.' in response.content


@pytest.mark.django_db
def test_catalog_and_detail_pages_render_their_loan_context(client):
    catalog = client.get('/ui/loans/')
    detail = client.get('/ui/loans/L1/')

    assert catalog.status_code == 200
    assert b'Loan L1' in catalog.content
    assert b'ana \xc2\xb7 ISBN 9780134685991' in catalog.content
    assert detail.status_code == 200
    assert b'Loan L1' in detail.content
    assert b'ana' in detail.content


@pytest.mark.django_db
def test_django_admin_route_is_not_installed(client):
    assert client.get('/admin/login/').status_code == 404
