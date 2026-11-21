from datetime import date
from types import SimpleNamespace

import pytest

from src.loans.repository import LoanRepository
from src.loans.services import (
    LoanAlreadyReturned,
    LoanInputError,
    LoanNotFound,
    lend_loan,
    return_loan,
)


@pytest.mark.parametrize(
    ('member', 'isbn', 'expected_errors'),
    [
        ('', '9780134685991', {'member': 'Enter a member name.'}),
        (' \t', '9780134685991', {'member': 'Enter a member name.'}),
        ('reader', '', {'isbn': 'Enter an ISBN.'}),
        ('reader', ' \t', {'isbn': 'Enter an ISBN.'}),
        (None, None, {'member': 'Enter a member name.', 'isbn': 'Enter an ISBN.'}),
    ],
)
def test_lending_rejects_empty_or_whitespace_required_fields(member, isbn, expected_errors):
    with pytest.raises(LoanInputError) as error:
        lend_loan(None, member, isbn, date(2026, 11, 20))

    assert error.value.errors == expected_errors


@pytest.mark.django_db
def test_lending_persists_values_exactly_and_sets_the_fourteen_day_term():
    loan = lend_loan(LoanRepository(), ' m1 ', ' 978-0 ', date(2026, 11, 20))

    assert loan.id == 'L4'
    assert loan.member == ' m1 '
    assert loan.isbn == ' 978-0 '
    assert loan.lent_on == date(2026, 11, 20)
    assert loan.due_on == date(2026, 12, 4)


@pytest.mark.django_db
def test_lending_api_returns_the_new_formatted_record(client, monkeypatch):
    monkeypatch.setattr('django.utils.timezone.localdate', lambda: date(2026, 11, 20))

    response = client.post('/loans', {'member': 'reader', 'isbn': '123'})

    assert response.status_code == 201
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == 'L4;reader;123;2026-11-20;2026-12-04;\n'


@pytest.mark.django_db
def test_lending_api_rejects_blank_fields_with_the_characterized_error(client):
    response = client.post('/loans', {'member': ' \t', 'isbn': ''})

    assert response.status_code == 400
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == 'member and isbn are required\n'


@pytest.mark.django_db
def test_lending_api_escapes_delimiters_in_the_created_record(client, monkeypatch):
    monkeypatch.setattr('django.utils.timezone.localdate', lambda: date(2026, 11, 20))

    response = client.post('/loans', {'member': 'reader; one', 'isbn': '978"0'})

    assert response.status_code == 201
    assert response.content.decode() == 'L4;"reader; one";"978""0";2026-11-20;2026-12-04;\n'


@pytest.mark.django_db
def test_return_use_case_marks_an_unreturned_loan_with_the_supplied_date():
    loan = return_loan(LoanRepository(), 'L1', date(2026, 11, 20))

    assert loan.returned_on == date(2026, 11, 20)


@pytest.mark.django_db
def test_return_use_case_rejects_an_unknown_loan():
    with pytest.raises(LoanNotFound):
        return_loan(LoanRepository(), 'missing', date(2026, 11, 20))


@pytest.mark.django_db
def test_return_use_case_rejects_repeat_without_replacing_the_original_date():
    original_date = date(2026, 1, 20)

    with pytest.raises(LoanAlreadyReturned):
        return_loan(LoanRepository(), 'L2', date(2026, 11, 20))

    assert LoanRepository().find('L2').returned_on == original_date


def test_return_use_case_handles_a_concurrent_return():
    class ConcurrentReturnRepository:
        def find(self, loan_id):
            return SimpleNamespace(returned_on=None)

        def return_if_unreturned(self, loan_id, returned_on):
            return None

    with pytest.raises(LoanAlreadyReturned):
        return_loan(ConcurrentReturnRepository(), 'L1', date(2026, 11, 20))


@pytest.mark.django_db
def test_return_api_persists_and_returns_the_formatted_loan(client, monkeypatch):
    monkeypatch.setattr('django.utils.timezone.localdate', lambda: date(2026, 11, 20))

    response = client.post('/loans/L1/return')

    assert response.status_code == 200
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == 'L1;ana;9780134685991;2026-01-02;2026-01-16;2026-11-20\n'


@pytest.mark.django_db
def test_return_api_returns_the_characterized_not_found_response(client):
    response = client.post('/loans/missing/return')

    assert response.status_code == 404
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == 'no such loan\n'


@pytest.mark.django_db
def test_repeat_return_api_answers_conflict_without_replacing_the_saved_date(client, monkeypatch):
    monkeypatch.setattr('django.utils.timezone.localdate', lambda: date(2026, 11, 20))

    response = client.post('/loans/L2/return')

    assert response.status_code == 409
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == 'loan already returned\n'
    assert LoanRepository().find('L2').returned_on == date(2026, 1, 20)


@pytest.mark.django_db
def test_new_loan_form_uses_the_reading_room_flow(client):
    response = client.get('/ui/loans/new/')

    assert response.status_code == 200
    assert b'Lend a book' in response.content
    assert b'Member name' in response.content
    assert b'ISBN' in response.content
    assert b'action="/ui/loans/"' in response.content


@pytest.mark.django_db
def test_lending_ui_stores_submitted_values_as_given(client, monkeypatch):
    monkeypatch.setattr('django.utils.timezone.localdate', lambda: date(2026, 11, 20))

    response = client.post('/ui/loans/', {'member': ' m1 ', 'isbn': ' 978-0 '})

    assert response.status_code == 302
    assert response['Location'] == '/ui/loans/'
    loan = LoanRepository().find('L4')
    assert loan.member == ' m1 '
    assert loan.isbn == ' 978-0 '
    assert loan.lent_on == date(2026, 11, 20)


@pytest.mark.django_db
def test_lending_ui_renders_field_errors_and_preserves_invalid_values(client):
    response = client.post('/ui/loans/', {'member': '  ', 'isbn': ''})

    assert response.status_code == 400
    assert b'Enter a member name.' in response.content
    assert b'Enter an ISBN.' in response.content
    assert b'name="member" value="  "' in response.content
    assert b'name="isbn" value=""' in response.content
    assert b'aria-invalid="true"' in response.content

    response = client.post('/ui/loans/', {'member': '', 'isbn': ' \t'})

    assert response.status_code == 400
    assert b'name="member" value=""' in response.content
    assert b'name="isbn" value=" \t"' in response.content


@pytest.mark.django_db
def test_unreturned_loan_detail_offers_an_htmx_return_action(client):
    response = client.get('/ui/loans/L1/')

    assert response.status_code == 200
    assert b'hx-post="/ui/loans/L1/return/"' in response.content
    assert b'csrfmiddlewaretoken' in response.content


@pytest.mark.django_db
def test_return_ui_updates_the_loan_with_the_return_date(client, monkeypatch):
    monkeypatch.setattr('django.utils.timezone.localdate', lambda: date(2026, 11, 20))

    response = client.post('/ui/loans/L1/return/', HTTP_HX_REQUEST='true')

    assert response.status_code == 200
    assert b'Returned Nov 20, 2026' in response.content
    assert b'hx-post=' not in response.content
    assert b'role="alert"' not in response.content


@pytest.mark.django_db
def test_repeat_return_ui_renders_error_and_preserves_saved_date(client, monkeypatch):
    monkeypatch.setattr('django.utils.timezone.localdate', lambda: date(2026, 11, 20))

    response = client.post('/ui/loans/L2/return/', HTTP_HX_REQUEST='true')

    assert response.status_code == 409
    assert (
        b'<p class="text-sm text-[#a94e37]" role="alert">This loan has already been returned.</p>'
        in response.content
    )
    assert b'Jan 20, 2026' in response.content
    assert b'hx-on::before-swap=' in response.content


@pytest.mark.django_db
def test_unknown_return_ui_renders_the_htmx_not_found_response(client):
    response = client.post('/ui/loans/missing/return/', HTTP_HX_REQUEST='true')

    assert response.status_code == 404
    assert b'<p class="text-sm text-[#a94e37]" role="alert">No such loan.</p>' in response.content
    assert b'hx-on::before-swap=' in response.content


@pytest.mark.django_db
def test_loan_collections_reject_unsupported_methods(client):
    api_response = client.put('/loans')
    browser_response = client.put('/ui/loans/')

    assert api_response.status_code == 405
    assert browser_response.status_code == 405


@pytest.mark.django_db
def test_loan_catalog_shows_seeded_records_and_lending_link(client):
    response = client.get('/ui/loans/')

    assert response.status_code == 200
    assert b'Loan L1' in response.content
    assert b'ana' in response.content
    assert b'href="/ui/loans/new/"' in response.content


@pytest.mark.django_db
def test_new_loan_form_only_accepts_get(client):
    response = client.post('/ui/loans/new/')

    assert response.status_code == 405


@pytest.mark.django_db
def test_return_endpoints_only_accept_post(client):
    api_response = client.get('/loans/L1/return')
    browser_response = client.get('/ui/loans/L1/return/')

    assert api_response.status_code == 405
    assert browser_response.status_code == 405
