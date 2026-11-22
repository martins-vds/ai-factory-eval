import pytest


@pytest.mark.django_db
def test_loan_list_page_shows_member_ids_and_due_dates(client):
    response = client.get('/ui/loans/')

    assert response.status_code == 200
    assert b'ana' in response.content
    assert b'L1' in response.content
    assert b'Jan 16, 2026' in response.content


@pytest.mark.django_db
def test_loan_detail_page_shows_dates(client):
    response = client.get('/ui/loans/L1/')

    assert response.status_code == 200
    assert b'Loan record' in response.content
    assert b'ana' in response.content
    assert b'9780134685991' in response.content
    assert b'L1' in response.content
    assert b'Jan 16, 2026' in response.content


@pytest.mark.django_db
def test_unknown_loan_page_renders_not_found_response(client):
    response = client.get('/ui/loans/unknown/')

    assert response.status_code == 404
    assert b'That loan is not in the ledger.' in response.content
