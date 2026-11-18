import json
from pathlib import Path

import pytest


HTTP_GOLDENS = json.loads(
    (
        Path(__file__).resolve().parents[2]
        / '.migration/characterization/source/goldens/http.json'
    ).read_text(encoding='utf-8')
)
EDGE_GOLDENS = json.loads(
    (
        Path(__file__).resolve().parents[2]
        / '.migration/characterization/source/goldens/edge-cases.json'
    ).read_text(encoding='utf-8')
)


@pytest.mark.django_db
def test_fee_api_returns_the_characterized_html(client):
    expected = HTTP_GOLDENS['GET /fees/{id}']['response']

    response = client.get('/fees/L3')

    assert response.status_code == expected['status']
    assert response['Content-Type'] == expected['content_type']
    assert response.content.decode() == expected['body']


@pytest.mark.django_db
def test_fee_api_returns_the_characterized_not_found_response(client):
    expected = EDGE_GOLDENS['GET /fees/unknown']['response']

    response = client.get('/fees/unknown')

    assert response.status_code == expected['status']
    assert response['Content-Type'] == expected['content_type']
    assert response.content.decode() == expected['body']


@pytest.mark.django_db
def test_reading_room_fee_page_shows_the_fee_and_htmx_payment_form(client):
    response = client.get('/ui/fees/L3/')

    assert response.status_code == 200
    assert b'Late fees</h1>' in response.content
    assert b'cy \xc2\xb7 L3' in response.content
    assert b'Dec 15, 2025' in response.content
    assert b'19 late days' in response.content
    assert b'$4.75' in response.content
    assert b'action="/ui/payments/L3/"' in response.content
    assert b'hx-post="/ui/payments/L3/"' in response.content
    assert b'Pay late fee' in response.content
