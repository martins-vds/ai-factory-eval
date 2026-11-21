from datetime import date

import pytest
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.db import IntegrityError
from django.urls import reverse
from django.utils import timezone

from src.loans.models import Loan
from src.loans.repository import LoanRepository
from src.loans.services import (
    LoanAlreadyReturnedError,
    RequiredLoanFieldError,
    lend_loan,
    return_loan,
)


@pytest.mark.django_db
def test_list_endpoint_returns_seeded_records(client):
    response = client.get('/loans')

    assert response.status_code == 200
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == (
        'L1;ana;9780134685991;2026-01-02;2026-01-16;\n'
        'L2;bo;9780596007126;2026-01-10;2026-01-24;2026-01-20\n'
        'L3;cy;9781617294945;2025-12-01;2025-12-15;2026-01-03\n'
    )


@pytest.mark.django_db
def test_detail_endpoint_returns_one_formatted_loan(client):
    response = client.get('/loans/L1')

    assert response.status_code == 200
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == 'L1;ana;9780134685991;2026-01-02;2026-01-16;\n'


@pytest.mark.django_db
def test_detail_endpoint_returns_not_found_for_unknown_loan(client):
    response = client.get('/loans/unknown')

    assert response.status_code == 404
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == 'no such loan\n'


@pytest.mark.django_db
def test_api_return_endpoint_returns_unknown_loan_error(client):
    response = client.post('/loans/unknown/return')

    assert response.status_code == 404
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == 'no such loan\n'


@pytest.mark.django_db
def test_saved_catalog_record_is_available_to_a_later_request(client):
    Loan.objects.create(
        id='L8',
        member='reader',
        isbn='123',
        lent_on=date(2026, 3, 1),
    )

    response = client.get('/loans/L8')

    assert response.status_code == 200
    assert response.content.decode() == 'L8;reader;123;2026-03-01;2026-03-15;\n'


@pytest.mark.django_db
def test_migration_startup_does_not_replace_persisted_records():
    loan = Loan.objects.get(pk='L1')
    loan.member = 'ada'
    loan.save(update_fields=['member'])

    call_command('migrate', interactive=False, verbosity=0)

    assert Loan.objects.get(pk='L1').member == 'ada'


@pytest.mark.django_db
def test_due_date_is_fourteen_calendar_days_after_lending():
    loan = Loan(
        id='L9',
        member='reader',
        isbn='123',
        lent_on=date(2024, 2, 15),
    )

    assert loan.due_on == date(2024, 2, 29)


@pytest.mark.django_db
def test_detail_export_quotes_delimiters_quotes_and_line_breaks(client):
    Loan.objects.create(
        id='L9',
        member='Reader; Example\nSecond line',
        isbn='978"xyz',
        lent_on=date(2026, 3, 1),
    )

    response = client.get('/loans/L9')

    assert response.status_code == 200
    assert response.content.decode() == (
        'L9;"Reader; Example\nSecond line";"978""xyz";2026-03-01;2026-03-15;\n'
    )


@pytest.mark.django_db
def test_model_enforces_required_fields_and_source_string_limits():
    with pytest.raises(ValidationError) as missing_fields:
        Loan(id='L9', member='', isbn='', lent_on=date(2026, 3, 1)).full_clean()

    assert set(missing_fields.value.message_dict) == {'member', 'isbn'}

    valid_maximum = Loan(
        id='I' * 255,
        member='M' * 255,
        isbn='B' * 255,
        lent_on=date(2026, 3, 1),
    )
    valid_maximum.full_clean()
    assert valid_maximum.due_on == date(2026, 3, 15)

    for field in ('id', 'member', 'isbn'):
        values = {'id': 'L9', 'member': 'reader', 'isbn': '123'}
        values[field] = 'x' * 256
        loan = Loan(**values, lent_on=date(2026, 3, 1))
        with pytest.raises(ValidationError) as long_field:
            loan.full_clean()
        assert field in long_field.value.message_dict


@pytest.mark.django_db
def test_unreturned_loan_is_valid():
    loan = Loan(id='L9', member='reader', isbn='123', lent_on=date(2026, 3, 1))

    loan.full_clean()
    returned_on = Loan._meta.get_field('returned_on')
    assert loan.returned_on is None
    assert loan.due_on == date(2026, 3, 15)
    assert returned_on.null
    assert returned_on.blank


@pytest.mark.django_db
def test_list_endpoint_orders_all_records_by_id(client):
    Loan.objects.create(
        id='L10',
        member='reader',
        isbn='123',
        lent_on=date(2026, 3, 1),
    )
    Loan.objects.create(
        id='L0',
        member='reader',
        isbn='456',
        lent_on=date(2026, 3, 1),
    )

    response = client.get('/loans')

    assert response.status_code == 200
    assert [line.split(';', 1)[0] for line in response.content.decode().splitlines()] == [
        'L0',
        'L1',
        'L10',
        'L2',
        'L3',
    ]


@pytest.mark.django_db
def test_browser_detail_page_shows_loan_dates(client):
    response = client.get('/ui/loans/L1/')

    assert response.status_code == 200
    assert b'Loan record \xc2\xb7 L1' in response.content
    assert b'Jan 2, 2026' in response.content
    assert b'Jan 16, 2026' in response.content


@pytest.mark.django_db
def test_repository_write_rolls_back_failed_transaction():
    with pytest.raises(IntegrityError):
        LoanRepository().create(
            id='L1',
            member='duplicate',
            isbn='123',
            lent_on=date(2026, 3, 1),
        )

    assert Loan.objects.get(pk='L1').member == 'ana'


@pytest.mark.django_db
def test_lend_endpoint_creates_loan_and_returns_fourteen_day_due_date(client, monkeypatch):
    monkeypatch.setattr(timezone, 'localdate', lambda: date(2026, 11, 21))

    response = client.post('/loans', {'member': 'dee', 'isbn': '123'})

    assert response.status_code == 201
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == 'L4;dee;123;2026-11-21;2026-12-05;\n'
    assert Loan.objects.get(pk='L4').due_on == date(2026, 12, 5)


@pytest.mark.django_db
@pytest.mark.parametrize(
    ('member', 'isbn'),
    [
        ('', '123'),
        ('  ', '123'),
        ('dee', ''),
        ('dee', '  '),
    ],
)
def test_lend_endpoint_rejects_blank_member_or_isbn(client, member, isbn):
    response = client.post('/loans', {'member': member, 'isbn': isbn})

    assert response.status_code == 400
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == 'member and isbn are required\n'


@pytest.mark.django_db
def test_lending_use_case_rejects_blank_fields():
    with pytest.raises(RequiredLoanFieldError):
        lend_loan('  ', '123', LoanRepository(), date(2026, 11, 21))


@pytest.mark.django_db
def test_return_use_case_rejects_repeat_and_preserves_original_date():
    loan = Loan.objects.get(pk='L2')
    original = loan.returned_on

    with pytest.raises(LoanAlreadyReturnedError):
        return_loan('L2', LoanRepository(), date(2026, 11, 21))

    loan.refresh_from_db()
    assert loan.returned_on == original


@pytest.mark.django_db
def test_return_endpoint_rejects_repeated_return_and_preserves_date(client, monkeypatch):
    monkeypatch.setattr(timezone, 'localdate', lambda: date(2026, 11, 21))

    first = client.post('/loans/L1/return')
    second = client.post('/loans/L1/return')

    assert first.status_code == 200
    assert first['Content-Type'] == 'text/plain'
    assert first.content.decode() == 'L1;ana;9780134685991;2026-01-02;2026-01-16;2026-11-21\n'
    assert second.status_code == 409
    assert second['Content-Type'] == 'text/plain'
    assert second.content.decode() == 'loan already returned\n'
    assert Loan.objects.get(pk='L1').returned_on == date(2026, 11, 21)


@pytest.mark.django_db
def test_browser_lend_page_rejects_blank_fields(client):
    get_response = client.get('/ui/loans/new/')

    assert get_response.status_code == 200
    assert b'Lend a book' in get_response.content

    post_response = client.post('/ui/loans/new/', {'member': '  ', 'isbn': '123'})

    assert post_response.status_code == 400
    assert b'Member and ISBN are required.' in post_response.content


@pytest.mark.django_db
def test_browser_return_rejects_repeated_return_and_keeps_original_date(client, monkeypatch):
    monkeypatch.setattr(timezone, 'localdate', lambda: date(2026, 11, 21))

    first = client.post('/ui/loans/L1/return/')
    second = client.post('/ui/loans/L1/return/')

    assert first.status_code == 302
    assert second.status_code == 409
    assert b'This loan has already been returned.' in second.content
    assert Loan.objects.get(pk='L1').returned_on == date(2026, 11, 21)


@pytest.mark.django_db
def test_browser_lend_creates_a_redirected_detail(client, monkeypatch):
    monkeypatch.setattr(timezone, 'localdate', lambda: date(2026, 11, 21))

    response = client.post('/ui/loans/new/', {'member': 'dee', 'isbn': '123'})

    assert response.status_code == 302
    assert response['Location'] == '/ui/loans/L4/'
    assert Loan.objects.get(pk='L4').member == 'dee'


@pytest.mark.django_db
def test_browser_catalog_lists_loan_records(client):
    response = client.get('/ui/loans/')

    assert response.status_code == 200
    assert b'Books in good company.' in response.content
    assert b'Loan L1' in response.content


@pytest.mark.django_db
def test_browser_return_unknown_loan_renders_not_found(client):
    response = client.post('/ui/loans/unknown/return/')

    assert response.status_code == 404
    assert b'Loan not found.' in response.content


@pytest.mark.django_db
def test_repository_next_id_uses_the_next_record_number():
    Loan.objects.create(
        id='L4',
        member='reader',
        isbn='123',
        lent_on=date(2026, 3, 1),
    )

    assert LoanRepository().next_id() == 'L5'


def test_ui_routes_have_stable_reverse_names():
    assert reverse('loan_catalog') == '/ui/loans/'
    assert reverse('loan_new') == '/ui/loans/new/'
    assert reverse('loan_catalog_detail', kwargs={'loan_id': 'L1'}) == '/ui/loans/L1/'
    assert reverse('loan_return_ui', kwargs={'loan_id': 'L1'}) == '/ui/loans/L1/return/'
