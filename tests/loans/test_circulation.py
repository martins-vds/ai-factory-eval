from datetime import timedelta

import pytest
from django.utils import timezone


@pytest.mark.django_db
def test_lend_endpoint_creates_a_loan_with_a_fourteen_day_due_date(client):
    lent_on = timezone.localdate()

    response = client.post('/loans', {'member': 'dee', 'isbn': '123'})

    assert response.status_code == 201
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == (
        f'L4;dee;123;{lent_on.isoformat()};{(lent_on + timedelta(days=14)).isoformat()};\n'
    )
    assert client.get('/loans/L4').content == response.content


@pytest.mark.parametrize(
    'form',
    [
        {'member': 'reader'},
        {'isbn': '123'},
        {'member': '', 'isbn': '123'},
        {'member': '  ', 'isbn': '123'},
        {'member': 'reader', 'isbn': ''},
        {'member': 'reader', 'isbn': ' \t '},
    ],
)
@pytest.mark.django_db
def test_lend_endpoint_rejects_missing_or_blank_fields(client, form):
    response = client.post('/loans', form)

    assert response.status_code == 400
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == 'member and isbn are required\n'
    assert len(client.get('/loans').content.decode().splitlines()) == 3


@pytest.mark.django_db
def test_return_endpoint_records_today_and_returns_the_updated_loan(client):
    returned_on = timezone.localdate()

    response = client.post('/loans/L1/return')

    assert response.status_code == 200
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == (
        f'L1;ana;9780134685991;2026-01-02;2026-01-16;{returned_on.isoformat()}\n'
    )
    assert client.get('/loans/L1').content == response.content


@pytest.mark.django_db
def test_return_endpoint_rejects_repeated_returns_without_replacing_the_date(client):
    first_response = client.post('/loans/L1/return')

    response = client.post('/loans/L1/return')

    assert response.status_code == 409
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == 'loan already returned\n'
    assert client.get('/loans/L1').content == first_response.content


@pytest.mark.django_db
def test_return_endpoint_returns_not_found_for_unknown_loan(client):
    response = client.post('/loans/unknown/return')

    assert response.status_code == 404
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == 'no such loan\n'


@pytest.mark.django_db
def test_browser_lend_form_reports_a_field_error_for_whitespace(client):
    response = client.post('/ui/loans/new/', {'member': ' \t ', 'isbn': '123'})

    assert response.status_code == 200
    assert b'Member is required.' in response.content
    assert b'aria-invalid="true"' in response.content


@pytest.mark.django_db
def test_htmx_lend_response_links_to_the_new_loan(client):
    response = client.post(
        '/ui/loans/new/',
        {'member': 'reader', 'isbn': '123'},
        headers={'HX-Request': 'true'},
    )

    assert response.status_code == 200
    assert b'id="loan-form"' in response.content
    assert b'href="/ui/loans/L4/"' in response.content


@pytest.mark.django_db
def test_htmx_return_response_replaces_the_return_action(client):
    response = client.post(
        '/ui/loans/L1/return/',
        headers={'HX-Request': 'true'},
    )

    assert response.status_code == 200
    assert b'id="return-action"' in response.content
    assert b'Returned today.' in response.content
