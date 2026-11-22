from datetime import date

import pytest

from src.loans.domain import Loan


def test_due_date_is_fourteen_calendar_days_after_lending():
    loan = Loan(
        loan_id='L1',
        member='ana',
        isbn='9780134685991',
        lent_on=date(2026, 1, 2),
        returned_on=None,
    )

    assert loan.due_on == date(2026, 1, 16)


@pytest.mark.django_db
def test_loan_list_matches_characterized_text(client):
    response = client.get('/loans')

    assert response.status_code == 200
    assert response['Content-Type'] == 'text/plain; charset=utf-8'
    assert response.content.decode() == (
        'L1;ana;9780134685991;2026-01-02;2026-01-16;\n'
        'L2;bo;9780596007126;2026-01-10;2026-01-24;2026-01-20\n'
        'L3;cy;9781617294945;2025-12-01;2025-12-15;2026-01-03\n'
    )


@pytest.mark.django_db
def test_loan_lookup_returns_characterized_line_or_not_found(client):
    found = client.get('/loans/L1')
    missing = client.get('/loans/unknown')

    assert found.status_code == 200
    assert found.content.decode() == 'L1;ana;9780134685991;2026-01-02;2026-01-16;\n'
    assert missing.status_code == 404
    assert missing.content.decode() == 'no such loan\n'
