import csv
from io import StringIO

import pytest
from django.urls import reverse

from src.loans.models import Loan


@pytest.mark.django_db
def test_seeded_loans_are_listed_in_id_order(client):
    response = client.get('/loans')

    assert response.status_code == 200
    assert response['Content-Type'].startswith('text/plain')
    assert response.content.decode() == (
        'L1;ana;9780134685991;2026-01-02;2026-01-16;\n'
        'L2;bo;9780596007126;2026-01-10;2026-01-24;2026-01-20\n'
        'L3;cy;9781617294945;2025-12-01;2025-12-15;2026-01-03\n'
    )


@pytest.mark.django_db
def test_loan_lookup_returns_one_line_or_characterized_not_found(client):
    response = client.get('/loans/L1')

    assert response.status_code == 200
    assert response.content.decode() == 'L1;ana;9780134685991;2026-01-02;2026-01-16;\n'

    missing = client.get('/loans/unknown')
    assert missing.status_code == 404
    assert missing.content.decode() == 'no such loan\n'


@pytest.mark.django_db
def test_export_quotes_delimiters_and_record_breaks(client):
    Loan.objects.create(
        id='L9',
        member='Member; One',
        isbn='123\n456',
        lent_on='2026-01-01',
        returned_on=None,
    )

    response = client.get('/loans')

    rows = list(csv.reader(StringIO(response.content.decode()), delimiter=';'))
    assert rows[-1] == ['L9', 'Member; One', '123\n456', '2026-01-01', '2026-01-15', '']


@pytest.mark.django_db
def test_catalog_pages_render_in_separate_ui_routes(client):
    response = client.get(reverse('loans:ui-list'))

    assert response.status_code == 200
    assert b'Lending Library' in response.content
    assert b'9780134685991' in response.content
    assert b'/loans/L1' in response.content

    detail = client.get(reverse('loans:ui-detail', kwargs={'loan_id': 'L1'}))
    assert detail.status_code == 200
    assert b'2026-01-16' in detail.content

