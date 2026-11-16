from datetime import date, timedelta

import pytest

from src.loans.models import Loan


@pytest.mark.django_db
def test_lending_api_creates_and_formats_a_loan(client):
    response = client.post('/loans', {'member': 'dee', 'isbn': '123'})

    today = date.today()
    due_on = today + timedelta(days=14)
    assert response.status_code == 201
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == f'L4;dee;123;{today};{due_on};\n'


@pytest.mark.django_db
def test_return_api_records_and_formats_today(client):
    response = client.post('/loans/L1/return')

    today = date.today()
    assert response.status_code == 200
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == (f'L1;ana;9780134685991;2026-01-02;2026-01-16;{today}\n')
    assert Loan.objects.get(pk='L1').returned_on == today


@pytest.mark.django_db
def test_return_api_rejects_repeated_return_without_replacing_date(client):
    response = client.post('/loans/L2/return')

    assert response.status_code == 409
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == 'loan already returned\n'
    assert Loan.objects.get(pk='L2').returned_on == date(2026, 1, 20)


@pytest.mark.django_db
def test_return_api_preserves_not_found_response(client):
    response = client.post('/loans/unknown/return')

    assert response.status_code == 404
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == 'no such loan\n'


@pytest.mark.django_db
def test_return_api_does_not_mutate_on_get(client):
    response = client.get('/loans/L1/return')

    assert response.status_code == 405
    assert Loan.objects.get(pk='L1').returned_on is None


@pytest.mark.django_db
def test_reading_room_lists_lending_and_return_actions(client):
    response = client.get('/ui/loans/')

    assert response.status_code == 200
    assert b'Lend a book' in response.content
    assert b'action="/ui/loans/new/"' in response.content
    assert b'action="/ui/loans/L1/return/"' in response.content
    assert b'hx-boost="true"' in response.content


@pytest.mark.django_db
def test_reading_room_rejects_blank_fields_with_field_errors(client):
    response = client.post(
        '/ui/loans/new/',
        {'member': '  ', 'isbn': ''},
        HTTP_HX_REQUEST='true',
    )

    assert response.status_code == 200
    assert b'Enter a member name; blank values are not accepted.' in response.content
    assert b'Enter an ISBN; blank values are not accepted.' in response.content
    assert b'aria-invalid="true"' in response.content
    assert Loan.objects.count() == 3


@pytest.mark.django_db
def test_lending_api_rejects_blank_values_without_creating_a_loan(client):
    response = client.post('/loans', {'member': '  ', 'isbn': '123'})

    assert response.status_code == 400
    assert response.content.decode() == 'member and isbn are required\n'
    assert Loan.objects.count() == 3


@pytest.mark.django_db
def test_reading_room_lends_a_book_through_htmx(client):
    response = client.post(
        '/ui/loans/new/',
        {'member': 'dee', 'isbn': '123'},
        HTTP_HX_REQUEST='true',
    )

    today = date.today()
    assert response.status_code == 200
    assert b'Loan L4 added to the collection.' in response.content
    assert b'Loan L4' in response.content
    assert Loan.objects.get(pk='L4').lent_on == today


@pytest.mark.django_db
def test_reading_room_lending_works_without_htmx(client):
    response = client.post(
        '/ui/loans/new/',
        {'member': 'dee', 'isbn': '123'},
        follow=True,
    )

    assert response.status_code == 200
    assert b'Loan L4 added to the collection.' in response.content
    assert Loan.objects.get(pk='L4').member == 'dee'


@pytest.mark.django_db
def test_reading_room_returns_once_and_keeps_the_original_date(client):
    response = client.post(
        '/ui/loans/L1/return/',
        HTTP_HX_REQUEST='true',
    )

    today = date.today()
    assert response.status_code == 200
    assert b'L1 marked returned today.' in response.content
    assert Loan.objects.get(pk='L1').returned_on == today

    response = client.post(
        '/ui/loans/L1/return/',
        HTTP_HX_REQUEST='true',
    )

    assert response.status_code == 200
    assert (
        f'L1 was already returned on {today}; repeat return rejected'.encode() in response.content
    )
    assert Loan.objects.get(pk='L1').returned_on == today
