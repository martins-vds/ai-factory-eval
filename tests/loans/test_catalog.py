import pytest


SEED_EXPORT = (
    'L1;ana;9780134685991;2026-01-02;2026-01-16;\n'
    'L2;bo;9780596007126;2026-01-10;2026-01-24;2026-01-20\n'
    'L3;cy;9781617294945;2025-12-01;2025-12-15;2026-01-03\n'
)


@pytest.mark.django_db
def test_list_returns_seeded_loans_in_characterized_format(client):
    response = client.get('/loans')

    assert response.status_code == 200
    assert response['Content-Type'] == 'text/plain; charset=utf-8'
    assert response.content.decode() == SEED_EXPORT


@pytest.mark.django_db
def test_get_returns_one_loan_with_trailing_newline(client):
    response = client.get('/loans/L1')

    assert response.status_code == 200
    assert response.content.decode() == 'L1;ana;9780134685991;2026-01-02;2026-01-16;\n'


@pytest.mark.django_db
def test_get_missing_loan_returns_characterized_not_found_response(client):
    response = client.get('/loans/missing')

    assert response.status_code == 404
    assert response.content.decode() == 'no such loan\n'
