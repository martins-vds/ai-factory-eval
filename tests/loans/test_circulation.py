from datetime import date, timedelta

import pytest

from src.loans.models import Loan


@pytest.mark.django_db
def test_lending_endpoint_creates_a_loan_with_the_characterized_record(client):
    lent_on = date.today()

    response = client.post('/loans', {'member': 'dee', 'isbn': '123'})

    assert response.status_code == 201
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == (
        f'L4;dee;123;{lent_on.isoformat()};{(lent_on + timedelta(days=14)).isoformat()};\n'
    )
    loan = Loan.objects.get(pk='L4')
    assert loan.member == 'dee'
    assert loan.isbn == '123'
    assert loan.lent_on == lent_on


@pytest.mark.django_db
def test_return_endpoint_records_today_and_returns_the_updated_loan(client):
    returned_on = date.today()

    response = client.post('/loans/L1/return')

    assert response.status_code == 200
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == (
        f'L1;ana;9780134685991;2026-01-02;2026-01-16;{returned_on.isoformat()}\n'
    )
    assert Loan.objects.get(pk='L1').returned_on == returned_on


@pytest.mark.parametrize(
    'form_data',
    [
        {'isbn': '123'},
        {'member': 'reader'},
        {'member': '', 'isbn': '123'},
        {'member': 'reader', 'isbn': ''},
        {'member': '   ', 'isbn': '123'},
        {'member': 'reader', 'isbn': '   '},
    ],
)
@pytest.mark.django_db
def test_lending_endpoint_rejects_missing_or_blank_fields(client, form_data):
    response = client.post('/loans', form_data)

    assert response.status_code == 400
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == 'member and isbn are required\n'
    assert Loan.objects.count() == 3


@pytest.mark.django_db
def test_return_endpoint_rejects_repeat_without_replacing_return_date(client):
    original_return_date = Loan.objects.get(pk='L2').returned_on

    response = client.post('/loans/L2/return')

    assert response.status_code == 409
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == 'loan already returned\n'
    assert Loan.objects.get(pk='L2').returned_on == original_return_date


@pytest.mark.django_db
def test_return_endpoint_returns_not_found_for_unknown_loan(client):
    response = client.post('/loans/unknown/return')

    assert response.status_code == 404
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == 'no such loan\n'


@pytest.mark.django_db
def test_new_loan_page_presents_a_reading_room_lending_form(client):
    response = client.get('/ui/loans/new/')

    assert response.status_code == 200
    assert b'Lend a book' in response.content
    assert b'name="member"' in response.content
    assert b'name="isbn"' in response.content


@pytest.mark.django_db
def test_new_loan_page_shows_field_errors_for_blank_values(client):
    response = client.post('/ui/loans/new/', {'member': '   ', 'isbn': ''})

    assert response.status_code == 200
    assert b'Enter a member name; blank values are not accepted.' in response.content
    assert b'Enter an ISBN; blank values are not accepted.' in response.content
    assert Loan.objects.count() == 3


@pytest.mark.django_db
def test_new_loan_page_creates_a_loan_and_redirects_to_collection(client):
    lent_on = date.today()

    response = client.post('/ui/loans/new/', {'member': 'dee', 'isbn': '123'})

    assert response.status_code == 302
    assert response['Location'] == '/ui/loans/'
    loan = Loan.objects.get(pk='L4')
    assert loan.member == 'dee'
    assert loan.isbn == '123'
    assert loan.lent_on == lent_on
    assert loan.due_on == lent_on + timedelta(days=14)


@pytest.mark.django_db
def test_loan_detail_page_uses_ui_path_for_htmx_return(client):
    response = client.get('/ui/loans/L1/')

    assert response.status_code == 200
    assert b'hx-post="/ui/loans/L1/return/"' in response.content


@pytest.mark.django_db
def test_htmx_return_updates_the_loan_and_redirects_to_its_detail(client):
    returned_on = date.today()

    response = client.post('/ui/loans/L1/return/', HTTP_HX_REQUEST='true')

    assert response.status_code == 204
    assert response['HX-Redirect'] == '/ui/loans/L1/'
    assert Loan.objects.get(pk='L1').returned_on == returned_on


@pytest.mark.django_db
def test_htmx_repeat_return_keeps_original_date_and_reports_rejection(client):
    original_return_date = Loan.objects.get(pk='L2').returned_on

    response = client.post('/ui/loans/L2/return/', HTTP_HX_REQUEST='true')

    assert response.status_code == 204
    assert Loan.objects.get(pk='L2').returned_on == original_return_date
    detail = client.get(response['HX-Redirect'])
    assert b'was already returned; the original return date was retained.' in detail.content
