import pytest
from django.apps import apps


def test_loan_app_uses_configured_default_primary_key_type():
    assert apps.get_app_config('loans').default_auto_field == 'django.db.models.BigAutoField'


@pytest.mark.django_db
def test_list_loans_returns_characterized_export(client):
    response = client.get('/loans')

    assert response.status_code == 200
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == (
        'L1;ana;9780134685991;2026-01-02;2026-01-16;\n'
        'L2;bo;9780596007126;2026-01-10;2026-01-24;2026-01-20\n'
        'L3;cy;9781617294945;2025-12-01;2025-12-15;2026-01-03\n'
    )


@pytest.mark.django_db
def test_get_loan_returns_characterized_line(client):
    response = client.get('/loans/L1')

    assert response.status_code == 200
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == 'L1;ana;9780134685991;2026-01-02;2026-01-16;\n'


@pytest.mark.django_db
def test_get_unknown_loan_returns_characterized_not_found(client):
    response = client.get('/loans/unknown')

    assert response.status_code == 404
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == 'no such loan\n'


@pytest.mark.django_db
def test_admin_route_is_not_installed(client):
    assert client.get('/admin/').status_code == 404
