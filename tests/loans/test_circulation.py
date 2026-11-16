from datetime import timedelta

import pytest
from django.utils import timezone


@pytest.mark.django_db
def test_lending_creates_a_fourteen_day_loan_and_returns_its_api_record(client):
    lent_on = timezone.localdate()

    response = client.post('/loans', {'member': 'dee', 'isbn': '123'})

    assert response.status_code == 201
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == (
        f'L4;dee;123;{lent_on.isoformat()};{(lent_on + timedelta(days=14)).isoformat()};\n'
    )
    assert client.get('/loans/L4').content.decode() == response.content.decode()


@pytest.mark.django_db
def test_lending_preserves_whitespace_around_nonblank_fields(client):
    lent_on = timezone.localdate()

    response = client.post('/loans', {'member': ' dee ', 'isbn': ' 123 '})

    assert response.status_code == 201
    assert response.content.decode() == (
        f'L4; dee ; 123 ;{lent_on.isoformat()};'
        f'{(lent_on + timedelta(days=14)).isoformat()};\n'
    )


@pytest.mark.django_db
def test_returning_a_loan_sets_today_and_returns_its_api_record(client):
    returned_on = timezone.localdate()

    response = client.post('/loans/L1/return')

    assert response.status_code == 200
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == (
        f'L1;ana;9780134685991;2026-01-02;2026-01-16;{returned_on.isoformat()}\n'
    )
    assert client.get('/loans/L1').content.decode() == response.content.decode()


@pytest.mark.django_db
def test_new_loan_page_offers_a_form_posting_to_the_ui_route(client):
    response = client.get('/ui/loans/new/')

    assert response.status_code == 200
    assert (
        b'<h1 class="mb-4 mt-3 text-5xl md:text-6xl">A new loan, carefully noted.</h1>'
        in response.content
    )
    assert b'<form action="/ui/loans/" method="post" hx-post="/ui/loans/">' in response.content
    assert b'name="member"' in response.content
    assert b'name="isbn"' in response.content


@pytest.mark.parametrize(
    'fields',
    [
        {'isbn': '123'},
        {'member': 'dee'},
        {'member': ' ', 'isbn': '123'},
        {'member': 'dee', 'isbn': '\t'},
    ],
)
@pytest.mark.django_db
def test_api_lending_rejects_missing_and_blank_fields(client, fields):
    response = client.post('/loans', fields)

    assert response.status_code == 400
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == 'member and isbn are required\n'


@pytest.mark.django_db
def test_repeated_api_return_preserves_the_original_return_date(client):
    response = client.post('/loans/L2/return')

    assert response.status_code == 409
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == 'loan already returned\n'
    assert client.get('/loans/L2').content.decode() == (
        'L2;bo;9780596007126;2026-01-10;2026-01-24;2026-01-20\n'
    )


@pytest.mark.django_db
def test_browser_lending_creates_a_loan_and_redirects_to_its_record(client):
    response = client.post('/ui/loans/', {'member': 'dee', 'isbn': '123'})

    assert response.status_code == 302
    assert response['Location'] == '/ui/loans/L4/'
    detail = client.get(response['Location'])
    assert detail.status_code == 200
    assert b'dee \xc2\xb7 ISBN 123' in detail.content


@pytest.mark.django_db
def test_browser_lending_shows_field_errors_for_blank_values(client):
    response = client.post('/ui/loans/', {'member': ' ', 'isbn': '123'})

    assert response.status_code == 400
    assert b'name="member"' in response.content
    assert b'This field is required.' in response.content


@pytest.mark.django_db
def test_browser_return_updates_the_record_and_hides_the_return_action(client):
    returned_on = timezone.localdate()

    response = client.post('/ui/loans/L1/return/')

    assert response.status_code == 302
    assert response['Location'] == '/ui/loans/L1/'
    detail = client.get(response['Location'])
    returned_date = f'{returned_on.strftime("%b")} {returned_on.day}, {returned_on.year}'
    assert b'<dt class="text-sm text-[#66705b]">Returned</dt>' in detail.content
    assert f'<dd>{returned_date}</dd>'.encode() in detail.content
    assert b'Mark as returned' not in detail.content


@pytest.mark.django_db
def test_browser_repeat_return_is_rejected_without_changing_the_date(client):
    response = client.post('/ui/loans/L2/return/')

    assert response.status_code == 409
    assert b'This book has already been returned.' in response.content
    assert b'Jan 20, 2026' in response.content
    assert b'Mark as returned' not in response.content


@pytest.mark.django_db
def test_unreturned_loan_page_offers_a_ui_return_action(client):
    response = client.get('/ui/loans/L1/')

    assert response.status_code == 200
    assert b'action="/ui/loans/L1/return/"' in response.content
    assert b'hx-post="/ui/loans/L1/return/"' in response.content
    assert b'Mark as returned' in response.content


@pytest.mark.django_db
def test_api_return_of_unknown_loan_preserves_the_characterized_response(client):
    response = client.post('/loans/unknown/return')

    assert response.status_code == 404
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == 'no such loan\n'


@pytest.mark.parametrize(
    'return_path',
    ['/loans/L1/return', '/ui/loans/L1/return/'],
)
@pytest.mark.django_db
def test_return_routes_reject_get_requests_without_mutating_the_loan(
    client, return_path
):
    response = client.get(return_path)

    assert response.status_code == 405
    assert client.get('/loans/L1').content.decode() == (
        'L1;ana;9780134685991;2026-01-02;2026-01-16;\n'
    )
