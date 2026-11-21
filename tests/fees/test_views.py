from datetime import date

import pytest

from src.loans.models import Loan


@pytest.mark.django_db
def test_fee_api_returns_the_characterized_html(client):
    Loan.objects.create(
        id='L9',
        member='reader',
        isbn='123',
        lent_on=date(2025, 12, 1),
        returned_on=date(2026, 1, 3),
    )

    response = client.get('/fees/L9')

    assert response.status_code == 200
    assert response['Content-Type'].split(';', 1)[0] == 'text/html'
    assert response.content.decode() == (
        '<h1>Late fee for L9</h1><p>Due 2025-12-15, 19 day(s) late.</p>'
        '<p class="fee">Fee: $4.75</p>'
    )


@pytest.mark.django_db
def test_fee_api_returns_characterized_not_found_response(client):
    response = client.get('/fees/unknown')

    assert response.status_code == 404
    assert response['Content-Type'].split(';', 1)[0] == 'text/html'
    assert response.content == b'<p>No such loan.</p>'
