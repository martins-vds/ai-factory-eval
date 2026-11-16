import json
import re
from datetime import timedelta
from pathlib import Path

import pytest
from django.utils import timezone
from playwright.sync_api import sync_playwright

GOLDENS = Path(__file__).resolve().parents[2] / '.migration/characterization/source/goldens'


def characterized_response(filename, case):
    observations = json.loads((GOLDENS / filename).read_text(encoding='utf-8'))
    return observations[case]['response']


def normalize_dates(value):
    return re.sub(r'\d{4}-\d{2}-\d{2}', '<date>', value)


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
def test_lending_response_matches_the_characterized_http_golden(client):
    expected = characterized_response('http.json', 'POST /loans')
    request = json.loads((GOLDENS / 'http.json').read_text(encoding='utf-8'))['POST /loans'][
        'request'
    ]

    response = client.post(request['path'], request['form'])

    assert response.status_code == expected['status']
    assert response['Content-Type'] == expected['content_type']
    assert normalize_dates(response.content.decode()) == normalize_dates(expected['body'])


@pytest.mark.django_db
def test_lending_preserves_whitespace_around_nonblank_fields(client):
    lent_on = timezone.localdate()

    response = client.post('/loans', {'member': ' dee ', 'isbn': ' 123 '})

    assert response.status_code == 201
    assert response.content.decode() == (
        f'L4; dee ; 123 ;{lent_on.isoformat()};{(lent_on + timedelta(days=14)).isoformat()};\n'
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
def test_return_response_matches_the_characterized_http_golden(client):
    http = json.loads((GOLDENS / 'http.json').read_text(encoding='utf-8'))
    request = http['POST /loans/{id}/return']['request']
    expected = http['POST /loans/{id}/return']['response']

    response = client.post(request['path'])

    assert response.status_code == expected['status']
    assert response['Content-Type'] == expected['content_type']
    assert normalize_dates(response.content.decode()) == normalize_dates(expected['body'])


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
def test_blank_lending_applies_the_approved_fix_to_characterized_success(client):
    case = json.loads((GOLDENS / 'edge-cases.json').read_text(encoding='utf-8'))[
        'POST /loans/blank-fields'
    ]

    assert case['response']['status'] == 201
    response = client.post(case['request']['path'], case['request']['form'])

    assert response.status_code == 400
    assert response.content.decode() == 'member and isbn are required\n'


@pytest.mark.django_db
def test_repeated_api_return_preserves_the_original_return_date(client):
    case = json.loads((GOLDENS / 'edge-cases.json').read_text(encoding='utf-8'))[
        'POST /loans/L2/return again'
    ]

    assert case['response']['status'] == 200
    response = client.post(case['request']['path'])

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
def test_browser_can_lend_and_return_a_book(live_server):
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        try:
            page = browser.new_page()
            page.goto(f'{live_server.url}/ui/loans/new/')
            page.get_by_label('Member').fill('dee')
            page.get_by_label('Isbn').fill('123')
            page.get_by_role('button', name='Lend this book').click()
            page.get_by_text('dee · ISBN 123').wait_for()
            page.get_by_role('button', name='Mark as returned').click()
            page.get_by_role('button', name='Mark as returned').wait_for(state='detached')
            returned_on = timezone.localdate()
            returned_date = f'{returned_on.strftime("%b")} {returned_on.day}, {returned_on.year}'
            assert page.locator('dd').nth(2).inner_text() == returned_date
        finally:
            browser.close()


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
def test_return_routes_reject_get_requests_without_mutating_the_loan(client, return_path):
    response = client.get(return_path)

    assert response.status_code == 405
    assert client.get('/loans/L1').content.decode() == (
        'L1;ana;9780134685991;2026-01-02;2026-01-16;\n'
    )
