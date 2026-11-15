from datetime import date, timedelta

import pytest
from django.test import Client
from django.utils import timezone

from src.loans.models import Loan


@pytest.mark.django_db
def test_lending_creates_and_returns_the_characterized_record(client):
    response = client.post('/loans', {'member': 'dee', 'isbn': '123'})

    assert response.status_code == 201
    loan = Loan.objects.get(pk='L4')
    assert loan.member == 'dee'
    assert loan.isbn == '123'
    assert loan.lent_on == timezone.localdate()
    assert loan.due_on == loan.lent_on + timedelta(days=14)
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == (
        f'L4;dee;123;{loan.lent_on.isoformat()};{loan.due_on.isoformat()};\n'
    )


@pytest.mark.django_db
def test_api_lending_preserves_source_fields_but_quotes_export_delimiters(client):
    response = client.post(
        '/loans',
        {'member': 'a;b', 'isbn': '123\n456'},
    )

    loan = Loan.objects.get(pk='L4')
    assert response.status_code == 201
    assert loan.member == 'a;b'
    assert loan.isbn == '123\n456'
    assert response.content.decode() == (
        f'L4;"a;b";"123\n456";{loan.lent_on.isoformat()};{loan.due_on.isoformat()};\n'
    )


@pytest.mark.django_db
def test_api_lending_does_not_require_a_browser_csrf_token():
    response = Client(enforce_csrf_checks=True).post(
        '/loans',
        {'member': 'dee', 'isbn': '123'},
    )

    assert response.status_code == 201


@pytest.mark.django_db
def test_lending_preserves_nonblank_surrounding_whitespace(client):
    response = client.post('/loans', {'member': ' dee ', 'isbn': '123 '})

    loan = Loan.objects.get(pk='L4')
    assert response.status_code == 201
    assert loan.member == ' dee '
    assert loan.isbn == '123 '
    assert response.content.decode() == (
        f'L4; dee ;123 ;{loan.lent_on.isoformat()};{loan.due_on.isoformat()};\n'
    )


@pytest.mark.django_db
@pytest.mark.parametrize(
    'fields',
    [
        {'member': 'dee'},
        {'isbn': '123'},
        {'member': '', 'isbn': '123'},
        {'member': 'dee', 'isbn': ''},
        {'member': '  ', 'isbn': '123'},
        {'member': 'dee', 'isbn': '\t'},
        {'member': 'm' * 256, 'isbn': '123'},
        {'member': 'dee', 'isbn': 'i' * 256},
    ],
)
def test_lending_rejects_missing_or_blank_fields(client, fields):
    response = client.post('/loans', fields)

    assert response.status_code == 400
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == 'member and isbn are required\n'
    assert not Loan.objects.filter(pk='L4').exists()


@pytest.mark.django_db
def test_lending_form_shows_field_errors_for_blank_values(client):
    form_page = client.get('/ui/loans/new/')

    assert form_page.status_code == 200
    assert b'hx-post="/ui/loans/new/"' in form_page.content
    assert b'class="input input-bordered w-full"' in form_page.content
    assert b'ISBN' in form_page.content
    assert form_page.context['form'].fields['member'].max_length == 255
    assert form_page.context['form'].fields['isbn'].max_length == 255

    response = client.post('/ui/loans/new/', {'member': ' ', 'isbn': ''})

    assert response.status_code == 200
    assert response.context['form'].errors.keys() == {'member', 'isbn'}
    assert response.context['form'].errors['member'] == ['This field is required.']
    assert response.context['form'].errors['isbn'] == ['This field is required.']
    assert b'hx-post="/ui/loans/new/"' in response.content
    assert not Loan.objects.filter(pk='L4').exists()


@pytest.mark.django_db
def test_lending_form_creates_a_loan_and_redirects_htmx(client):
    response = client.post(
        '/ui/loans/new/',
        {'member': 'dee', 'isbn': '123'},
        HTTP_HX_REQUEST='true',
    )

    assert response.status_code == 200
    assert response['HX-Redirect'] == '/ui/loans/'
    loan = Loan.objects.get(pk='L4')
    assert loan.member == 'dee'
    assert loan.isbn == '123'
    assert loan.due_on == loan.lent_on + timedelta(days=14)


@pytest.mark.django_db
def test_lending_form_works_without_htmx_and_redirects_to_collection(client):
    response = client.post('/ui/loans/new/', {'member': 'dee', 'isbn': '123'})

    assert response.status_code == 302
    assert response['Location'] == '/ui/loans/'
    assert Loan.objects.get(pk='L4').member == 'dee'


@pytest.mark.django_db
def test_browser_catalog_lists_seeded_loans_and_links_to_lending_form(client):
    response = client.get('/ui/loans/')

    assert response.status_code == 200
    assert b'ana \xc2\xb7 ISBN 9780134685991' in response.content
    assert b'href="/ui/loans/new/"' in response.content


@pytest.mark.django_db
def test_lending_form_rejects_unsupported_methods(client):
    response = client.delete('/ui/loans/new/')

    assert response.status_code == 405


@pytest.mark.django_db
def test_return_updates_the_loan_and_records_the_date(client):
    response = client.post('/loans/L1/return')

    assert response.status_code == 200
    assert response['Content-Type'] == 'text/plain'
    returned_on = Loan.objects.get(pk='L1').returned_on
    assert returned_on == timezone.localdate()
    assert response.content.decode() == (
        f'L1;ana;9780134685991;2026-01-02;2026-01-16;{returned_on.isoformat()}\n'
    )


@pytest.mark.django_db
def test_repeat_return_rejects_request_and_preserves_existing_date(client):
    repeated = client.post('/loans/L2/return')

    assert repeated.status_code == 409
    assert repeated['Content-Type'] == 'text/plain'
    assert repeated.content.decode() == 'loan already returned\n'
    assert Loan.objects.get(pk='L2').returned_on == date(2026, 1, 20)


@pytest.mark.django_db
def test_return_reports_unknown_loan(client):
    response = client.post('/loans/unknown/return')

    assert response.status_code == 404
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == 'no such loan\n'


@pytest.mark.django_db
def test_api_return_rejects_get_without_mutating_the_loan(client):
    response = client.get('/loans/L1/return')

    assert response.status_code == 405
    assert Loan.objects.get(pk='L1').returned_on is None


@pytest.mark.django_db
def test_api_return_does_not_require_a_browser_csrf_token():
    response = Client(enforce_csrf_checks=True).post('/loans/L1/return')

    assert response.status_code == 200


@pytest.mark.django_db
def test_browser_return_rejects_get_and_preserves_the_unreturned_loan(client):
    response = client.get('/ui/loans/L1/return/')

    assert response.status_code == 405
    assert Loan.objects.get(pk='L1').returned_on is None


@pytest.mark.django_db
def test_browser_repeat_return_renders_conflict_and_keeps_original_date(client):
    response = client.post('/ui/loans/L2/return/')

    assert response.status_code == 409
    assert b'This loan has already been returned.' in response.content
    assert b'Returned' in response.content
    assert Loan.objects.get(pk='L2').returned_on == date(2026, 1, 20)


@pytest.mark.django_db
def test_ui_return_uses_htmx_and_updates_the_detail_page(client):
    detail = client.get('/ui/loans/L1/')

    assert detail.status_code == 200
    assert b'hx-post="/ui/loans/L1/return/"' in detail.content

    response = client.post('/ui/loans/L1/return/', HTTP_HX_REQUEST='true')

    assert response.status_code == 200
    assert response['HX-Redirect'] == '/ui/loans/L1/'
    assert Loan.objects.get(pk='L1').returned_on == timezone.localdate()


@pytest.mark.django_db
def test_browser_return_works_without_htmx_and_redirects_to_detail(client):
    response = client.post('/ui/loans/L1/return/')

    assert response.status_code == 302
    assert response['Location'] == '/ui/loans/L1/'
    assert Loan.objects.get(pk='L1').returned_on == timezone.localdate()


@pytest.mark.django_db
def test_browser_return_reports_unknown_loan(client):
    response = client.post('/ui/loans/unknown/return/')

    assert response.status_code == 404
