from datetime import date

import pytest
from django.core.exceptions import ValidationError
from django.urls import reverse

from src.loans.models import Loan


@pytest.mark.django_db(serialized_rollback=True)
def test_list_returns_seed_loans_as_ordered_semicolon_lines(client):
    list_path = reverse('loan-list')
    response = client.get(list_path)

    assert list_path == '/loans'
    assert response.status_code == 200
    assert response['Content-Type'].startswith('text/plain')
    assert response.content.decode() == (
        'L1;ana;9780134685991;2026-01-02;2026-01-16;\n'
        'L2;bo;9780596007126;2026-01-10;2026-01-24;2026-01-20\n'
        'L3;cy;9781617294945;2025-12-01;2025-12-15;2026-01-03\n'
    )


@pytest.mark.django_db(serialized_rollback=True)
def test_django_admin_is_not_exposed(client):
    assert client.get('/admin/login/').status_code == 404


@pytest.mark.django_db(serialized_rollback=True)
def test_get_returns_one_loan_or_the_legacy_not_found_response(client):
    detail_path = reverse('loan-detail', args=['L1'])
    found = client.get(detail_path)
    missing = client.get('/loans/unknown')

    assert detail_path == '/loans/L1'
    assert found.status_code == 200
    assert found['Content-Type'].startswith('text/plain')
    assert found.content.decode() == 'L1;ana;9780134685991;2026-01-02;2026-01-16;\n'
    assert missing.status_code == 404
    assert missing['Content-Type'].startswith('text/plain')
    assert missing.content.decode() == 'no such loan\n'


def test_due_date_is_fourteen_calendar_days_after_lending():
    loan = Loan(lent_on=date(2025, 12, 1))

    assert loan.due_on == date(2025, 12, 15)


@pytest.mark.parametrize('field', ('id', 'member', 'isbn'))
def test_loan_text_fields_keep_their_storage_limit(field):
    loan = Loan(id='L1', member='ana', isbn='123', lent_on=date(2026, 1, 2))
    setattr(loan, field, 'x' * 256)

    with pytest.raises(ValidationError):
        loan.full_clean(validate_unique=False, validate_constraints=False)


def test_return_date_is_optional():
    loan = Loan(id='L1', member='ana', isbn='123', lent_on=date(2026, 1, 2))

    Loan._meta.get_field('returned_on').validate(None, loan)
    loan.full_clean(validate_unique=False, validate_constraints=False)


@pytest.mark.django_db(serialized_rollback=True)
def test_export_quotes_field_and_record_delimiters(client):
    Loan.objects.create(
        id='L4',
        member='Member; One',
        isbn='123\n456',
        lent_on=date(2026, 3, 1),
    )

    response = client.get('/loans/L4')

    assert response.status_code == 200
    assert response.content.decode() == ('L4;"Member; One";"123\n456";2026-03-01;2026-03-15;\n')


@pytest.mark.django_db(serialized_rollback=True)
def test_catalog_renders_the_seed_records(client):
    catalog_path = reverse('loan-catalog')
    response = client.get(catalog_path)

    assert catalog_path == '/ui/loans/'
    assert response.status_code == 200
    assert 'Books in good company.' in response.content.decode()
    assert response.content.decode().count('<article') == 3


@pytest.mark.django_db(serialized_rollback=True)
def test_loan_record_is_persisted_and_available_through_api(client):
    Loan.objects.create(
        id='L4',
        member='dee',
        isbn='123',
        lent_on=date(2026, 11, 8),
    )

    response = client.get('/loans/L4')

    assert response.status_code == 200
    assert response.content.decode() == 'L4;dee;123;2026-11-08;2026-11-22;\n'
