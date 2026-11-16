import json
from datetime import date, timedelta
from pathlib import Path

import pytest
from django.utils import timezone

from src.fees.services import calculate_late_fee
from src.loans.models import Loan

HTTP_GOLDENS = (
    Path(__file__).resolve().parents[2] / '.migration/characterization/source/goldens/http.json'
)
EDGE_CASE_GOLDENS = (
    Path(__file__).resolve().parents[2]
    / '.migration/characterization/source/goldens/edge-cases.json'
)


def test_fee_is_waived_through_two_days_and_charged_at_twenty_five_cents_per_late_day():
    due_on = date(2026, 1, 16)

    two_days_late = calculate_late_fee(due_on, None, date(2026, 1, 18))
    three_days_late = calculate_late_fee(due_on, None, date(2026, 1, 19))

    assert (two_days_late.days_late, two_days_late.amount_cents) == (2, 0)
    assert (three_days_late.days_late, three_days_late.amount_cents) == (3, 75)


def test_fee_uses_return_date_and_never_exceeds_ten_dollars():
    due_on = date(2026, 1, 16)

    returned_early = calculate_late_fee(due_on, date(2026, 1, 15), date(2026, 11, 15))
    capped = calculate_late_fee(due_on, None, date(2027, 2, 20))

    assert (returned_early.days_late, returned_early.amount_cents) == (0, 0)
    assert capped.days_late > 40
    assert capped.amount_cents == 1000


@pytest.mark.django_db
def test_fee_api_returns_the_characterized_html(client):
    today = timezone.localdate()
    loan = Loan.objects.create(
        id='F1',
        member='reader',
        isbn='123',
        lent_on=today - timedelta(days=17),
    )

    response = client.get(f'/fees/{loan.id}')

    assert response.status_code == 200
    assert response['Content-Type'] == 'text/html'
    assert response.content.decode() == (
        f'<h1>Late fee for F1</h1><p>Due {loan.due_on.isoformat()}, 3 day(s) late.</p>'
        '<p class="fee">Fee: $0.75</p>'
    )


@pytest.mark.django_db
def test_fee_api_matches_the_source_golden_for_a_returned_loan(client):
    expected = json.loads(HTTP_GOLDENS.read_text(encoding='utf-8'))['GET /fees/{id}']['response']

    response = client.get('/fees/L3')

    assert response.status_code == expected['status']
    assert response['Content-Type'] == expected['content_type']
    assert response.content.decode() == expected['body']


@pytest.mark.django_db
def test_fee_api_matches_the_source_golden_for_a_capped_fee(client, monkeypatch):
    expected = json.loads(EDGE_CASE_GOLDENS.read_text(encoding='utf-8'))[
        'GET /fees/L1 before return'
    ]['response']
    monkeypatch.setattr('src.fees.views.timezone.localdate', lambda: date(2026, 11, 8))

    response = client.get('/fees/L1')

    assert response.status_code == expected['status']
    assert response['Content-Type'] == expected['content_type']
    assert response.content.decode() == expected['body']


@pytest.mark.django_db
def test_fee_api_returns_the_characterized_not_found_response(client):
    response = client.get('/fees/unknown')

    assert response.status_code == 404
    assert response['Content-Type'] == 'text/html'
    assert response.content.decode() == '<p>No such loan.</p>'


@pytest.mark.django_db
def test_reading_room_fee_page_shows_loan_fee_and_payment_action(client):
    today = timezone.localdate()
    loan = Loan.objects.create(
        id='F1',
        member='reader',
        isbn='123',
        lent_on=today - timedelta(days=17),
    )

    response = client.get(f'/ui/fees/{loan.id}/')

    assert response.status_code == 200
    assert b'A small nudge, never a surprise' in response.content
    assert b'Late fees' in response.content
    assert b'reader \xc2\xb7 F1' in response.content
    assert b'3 late days \xc2\xb7 first two days waived' in response.content
    assert b'$0.75' in response.content
    assert b'action="/ui/payments/F1/"' in response.content
    assert b'hx-post="/ui/payments/F1/"' in response.content


@pytest.mark.django_db
def test_reading_room_fee_page_shows_the_source_capped_amount(client):
    response = client.get('/ui/fees/L1/')

    assert response.status_code == 200
    assert b'$10.00' in response.content


@pytest.mark.django_db
def test_fee_api_rejects_non_get_methods(client):
    response = client.post('/fees/unknown')

    assert response.status_code == 405


@pytest.mark.django_db
def test_reading_room_fee_page_returns_not_found_for_an_unknown_loan(client):
    response = client.get('/ui/fees/unknown/')

    assert response.status_code == 404
    assert response['Content-Type'] == 'text/html'
    assert response.content.decode() == '<p>No such loan.</p>'


@pytest.mark.django_db
def test_reading_room_fee_page_rejects_non_get_methods(client):
    response = client.post('/ui/fees/L1/')

    assert response.status_code == 405
