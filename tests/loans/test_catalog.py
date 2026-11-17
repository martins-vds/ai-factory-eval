import pytest


@pytest.mark.django_db
def test_list_returns_seed_loans_as_characterized_text(client):
    response = client.get('/loans')

    assert response.status_code == 200
    assert response['Content-Type'].split(';', maxsplit=1)[0] == 'text/plain'
    assert response.content == (
        b'L1;ana;9780134685991;2026-01-02;2026-01-16;\n'
        b'L2;bo;9780596007126;2026-01-10;2026-01-24;2026-01-20\n'
        b'L3;cy;9781617294945;2025-12-01;2025-12-15;2026-01-03\n'
    )


@pytest.mark.django_db
def test_get_returns_one_loan_as_characterized_text(client):
    response = client.get('/loans/L1')

    assert response.status_code == 200
    assert response['Content-Type'].split(';', maxsplit=1)[0] == 'text/plain'
    assert response.content == b'L1;ana;9780134685991;2026-01-02;2026-01-16;\n'
