import json
from pathlib import Path

import pytest
from playwright.sync_api import sync_playwright

ABOUT_RESPONSE = json.loads(
    (
        Path(__file__).resolve().parents[2] / '.migration/characterization/source/goldens/http.json'
    ).read_text(encoding='utf-8')
)['GET /about']['response']


def test_about_endpoint_matches_characterized_response(client):
    response = client.get('/about')

    assert response.status_code == ABOUT_RESPONSE['status']
    assert response['Content-Type'] == ABOUT_RESPONSE['content_type']
    assert response.content.decode() == ABOUT_RESPONSE['body']


@pytest.mark.parametrize('path', ['/about', '/ui/about/'])
def test_about_pages_reject_non_get_requests(client, path):
    response = client.post(path)

    assert response.status_code == 405


@pytest.mark.django_db
def test_real_browser_renders_library_information(live_server):
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        try:
            page = browser.new_page()
            response = page.goto(f'{live_server.url}/ui/about/')

            assert response is not None
            assert response.status == 200
            assert page.get_by_role('heading', name='About the Lending Library').is_visible()
            assert page.get_by_text('Monday to Saturday, 9:00 to 18:00').is_visible()
            assert page.get_by_text('Books are lent for 14 days.').is_visible()
            contact = page.get_by_role('link', name='desk@lending-library.invalid')
            assert contact.is_visible()
            assert contact.get_attribute('href') == 'mailto:desk@lending-library.invalid'
        finally:
            browser.close()
