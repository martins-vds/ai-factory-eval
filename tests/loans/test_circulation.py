from datetime import timedelta

import pytest
from django.utils import timezone


@pytest.mark.django_db
def test_api_lending_creates_a_loan_with_a_fourteen_day_due_date(client):
    lent_on = timezone.localdate()

    response = client.post('/loans', {'member': 'dee', 'isbn': '123'})

    assert response.status_code == 201
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == (
        f'L4;dee;123;{lent_on.isoformat()};{(lent_on + timedelta(days=14)).isoformat()};\n'
    )


@pytest.mark.django_db
def test_api_return_records_today_and_persists_the_return_date(client):
    returned_on = timezone.localdate()

    response = client.post('/loans/L1/return')

    assert response.status_code == 200
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == (
        f'L1;ana;9780134685991;2026-01-02;2026-01-16;{returned_on.isoformat()}\n'
    )
    assert client.get('/loans/L1').content == response.content


@pytest.mark.django_db
@pytest.mark.parametrize(
    ('payload', 'field'),
    [
        ({}, 'member'),
        ({'member': 'dee'}, 'isbn'),
        ({'member': '', 'isbn': '123'}, 'member'),
        ({'member': 'dee', 'isbn': ''}, 'isbn'),
        ({'member': ' ', 'isbn': '123'}, 'member'),
        ({'member': 'dee', 'isbn': ' '}, 'isbn'),
    ],
)
def test_api_lending_rejects_missing_or_blank_fields(client, payload, field):
    response = client.post('/loans', payload)

    assert response.status_code == 400
    assert response['Content-Type'] == 'text/plain'
    assert field.encode() in response.content
    assert client.get('/loans').content.decode().count('\n') == 3


@pytest.mark.django_db
def test_api_lending_returns_field_errors_for_missing_values(client):
    response = client.post('/loans', {})

    assert response.status_code == 400
    assert response.content.decode() == (
        'member: This field is required.\nisbn: This field is required.'
    )


@pytest.mark.django_db
def test_api_repeated_return_is_rejected_without_replacing_the_original_date(client):
    response = client.post('/loans/L2/return')

    assert response.status_code == 409
    assert response['Content-Type'] == 'text/plain'
    assert response.content == b'already returned\n'
    assert client.get('/loans/L2').content == (
        b'L2;bo;9780596007126;2026-01-10;2026-01-24;2026-01-20\n'
    )


@pytest.mark.django_db
def test_api_return_of_unknown_loan_is_not_found(client):
    response = client.post('/loans/unknown/return')

    assert response.status_code == 404
    assert response['Content-Type'] == 'text/plain'
    assert response.content == b'no such loan\n'


@pytest.mark.django_db
def test_browser_can_lend_a_book_from_the_reading_room_page(client):
    lent_on = timezone.localdate()
    form_response = client.get('/ui/loans/new/')

    assert form_response.status_code == 200
    assert b'Lend a book' in form_response.content
    assert b'name="member"' in form_response.content
    assert b'name="isbn"' in form_response.content

    response = client.post('/ui/loans/new/', {'member': 'reader', 'isbn': '123'})

    assert response.status_code == 302
    assert response['Location'] == '/ui/loans/L4/'
    loan_detail = client.get(response['Location'])
    assert b'reader' in loan_detail.content
    assert lent_on.isoformat().encode() in loan_detail.content
