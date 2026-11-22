import pytest


@pytest.mark.django_db
def test_loan_detail_page_shows_dates(client):
    response = client.get('/ui/loans/L1/')

    assert response.status_code == 200
    assert b'Loan record' in response.content
    assert b'Jan 16, 2026' in response.content


@pytest.mark.django_db
def test_unknown_loan_page_renders_not_found_response(client):
    response = client.get('/ui/loans/unknown/')

    assert response.status_code == 404
    assert b'That loan is not in the ledger.' in response.content
