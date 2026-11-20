import pytest


@pytest.mark.django_db
def test_loan_catalog_ui_smoke(client):
    response = client.get('/ui/loans/')

    assert response.status_code == 200
    assert b'The Lending Library' in response.content
    assert b'L1' in response.content
