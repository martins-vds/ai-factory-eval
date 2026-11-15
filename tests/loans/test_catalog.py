from datetime import date

import pytest
from django.core.management import call_command
from django.test import Client

from src.loans.models import Loan
from src.loans.repository import save_loan


@pytest.mark.django_db
def test_loan_list_returns_the_seeded_text_export():
    response = Client().get('/loans')

    assert response.status_code == 200
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == (
        'L1;ana;9780134685991;2026-01-02;2026-01-16;\n'
        'L2;bo;9780596007126;2026-01-10;2026-01-24;2026-01-20\n'
        'L3;cy;9781617294945;2025-12-01;2025-12-15;2026-01-03\n'
    )


@pytest.mark.django_db
def test_loan_lookup_returns_a_formatted_record_or_characterized_not_found():
    client = Client()

    response = client.get('/loans/L1')
    assert response.status_code == 200
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == 'L1;ana;9780134685991;2026-01-02;2026-01-16;\n'

    missing = client.get('/loans/unknown')
    assert missing.status_code == 404
    assert missing['Content-Type'] == 'text/plain'
    assert missing.content.decode() == 'no such loan\n'


@pytest.mark.django_db
def test_loan_list_orders_records_by_identifier():
    for loan_id in ('L10', 'L4'):
        Loan.objects.create(
            id=loan_id,
            member='reader',
            isbn='123',
            lent_on=date(2026, 2, 20),
        )

    response = Client().get('/loans')
    loan_ids = [line.split(';', 1)[0] for line in response.content.decode().splitlines()]

    assert loan_ids == ['L1', 'L10', 'L2', 'L3', 'L4']


@pytest.mark.django_db
def test_due_date_is_fourteen_calendar_days_after_lending():
    loan = Loan.objects.get(pk='L1')

    assert loan.due_on == date(2026, 1, 16)


@pytest.mark.django_db
def test_text_export_escapes_semicolons_and_quotes_in_fields():
    Loan.objects.create(
        id='L4',
        member='a;"b',
        isbn='123;456',
        lent_on=date(2026, 2, 20),
    )

    response = Client().get('/loans')

    assert response.status_code == 200
    assert response.content.decode().endswith('L4;"a;""b";"123;456";2026-02-20;2026-03-06;\n')


@pytest.mark.django_db
def test_repository_write_commits_the_loan_record():
    loan = Loan(
        id='L4',
        member='dee',
        isbn='123',
        lent_on=date(2026, 2, 20),
    )

    saved_loan = save_loan(loan)

    assert saved_loan is loan
    assert Loan.objects.get(pk='L4') == loan


@pytest.mark.django_db
def test_repository_write_rolls_back_after_a_failure(monkeypatch):
    loan = Loan(
        id='L4',
        member='dee',
        isbn='123',
        lent_on=date(2026, 2, 20),
    )
    save = Loan.save

    def save_then_fail(instance, *args, **kwargs):
        save(instance, *args, **kwargs)
        raise RuntimeError('write interrupted')

    monkeypatch.setattr(Loan, 'save', save_then_fail)

    with pytest.raises(RuntimeError, match='write interrupted'):
        save_loan(loan)

    assert not Loan.objects.filter(pk='L4').exists()


@pytest.mark.django_db
def test_browser_detail_page_and_admin_removal():
    client = Client()

    detail = client.get('/ui/loans/L1/')
    assert detail.status_code == 200
    assert b'9780134685991' in detail.content
    assert b'Jan 16, 2026' in detail.content
    assert client.get('/ui/loans/unknown/').status_code == 404
    assert client.get('/admin/login/').status_code == 404


@pytest.mark.django_db
def test_persisted_records_survive_startup_migration():
    loan = Loan.objects.get(pk='L1')
    original_member = loan.member
    try:
        Loan.objects.filter(pk='L1').update(member='persisted member')
        call_command('migrate', interactive=False, verbosity=0)

        response = Client().get('/loans/L1')

        assert response.status_code == 200
        assert response.content.decode() == (
            'L1;persisted member;9780134685991;2026-01-02;2026-01-16;\n'
        )
    finally:
        Loan.objects.filter(pk='L1').update(member=original_member)
