import json
from pathlib import Path

import pytest
from playwright.sync_api import sync_playwright

HTTP_GOLDEN_PATH = (
    Path(__file__).resolve().parents[2] / '.migration/characterization/source/goldens/http.json'
)
HTTP_GOLDENS = json.loads(HTTP_GOLDEN_PATH.read_text(encoding='utf-8'))


def test_about_endpoint_matches_characterized_page(client):
    expected = HTTP_GOLDENS['GET /about']['response']

    response = client.get('/about')

    assert response.status_code == expected['status']
    assert response['Content-Type'] == expected['content_type']
    assert response.content.decode() == expected['body']


def test_about_page_presents_library_information(client):
    response = client.get('/ui/about/')

    assert response.status_code == 200
    assert b'About the Lending Library' in response.content
    assert b'Monday to Saturday' in response.content
    assert b'9:00 to 18:00' in response.content
    assert b'14 days' in response.content
    assert b'desk@lending-library.invalid' in response.content
    assert b'href="/ui/loans/"' in response.content


def test_about_routes_only_accept_get(client):
    assert client.post('/about').status_code == 405
    assert client.post('/ui/about/').status_code == 405


@pytest.mark.django_db
def test_about_page_renders_in_a_browser(live_server):
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        try:
            page = browser.new_page()
            response = page.goto(f'{live_server.url}/ui/about/')
            assert response is not None
            assert response.status == 200
            assert page.get_by_role('heading', name='About the Lending Library').is_visible()
            assert page.get_by_text('Monday to Saturday', exact=False).is_visible()
            assert page.get_by_text('Books are lent for 14 days.', exact=False).is_visible()
            assert page.get_by_role('link', name='Browse the collection').is_visible()
        finally:
            browser.close()
