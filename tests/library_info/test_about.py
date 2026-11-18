import json
from pathlib import Path

import pytest
from playwright.sync_api import sync_playwright

HTTP_GOLDEN_PATH = (
    Path(__file__).resolve().parents[2] / '.migration/characterization/source/goldens/http.json'
)
HTTP_GOLDENS = json.loads(HTTP_GOLDEN_PATH.read_text(encoding='utf-8'))


def test_about_endpoint_matches_characterized_response(client):
    expected = HTTP_GOLDENS['GET /about']['response']

    response = client.get('/about')

    assert response.status_code == expected['status']
    assert response['Content-Type'] == expected['content_type']
    assert response.content.decode() == expected['body']


@pytest.mark.parametrize('path', ['/about', '/ui/about/'])
def test_about_pages_only_allow_get(client, path):
    response = client.post(path)

    assert response.status_code == 405


@pytest.mark.django_db
def test_real_browser_renders_the_reading_room_about_page(live_server):
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        try:
            page = browser.new_page()
            response = page.goto(f'{live_server.url}/ui/about/')

            assert response is not None
            assert response.status == 200
            assert page.get_by_role('heading', name='About the Lending Library').is_visible()
            assert page.get_by_text('Open Monday to Saturday, 9:00 to 18:00.').is_visible()
            assert page.get_by_text('Books are lent for 14 days.').is_visible()
            assert (
                page.get_by_role('link', name='desk@lending-library.invalid').get_attribute('href')
                == 'mailto:desk@lending-library.invalid'
            )
            assert page.locator('link[href="/static/css/tailwind.css"]').count() == 1
            assert page.locator('link[href*="daisyui@4.12.24"]').count() == 1
            assert page.locator('script[src*="htmx.org@2.0.11"]').count() == 1
            assert page.locator('body').get_attribute('class') == (
                'min-h-screen bg-[#f5f0e5] text-[#2f3428] font-serif'
            )
        finally:
            browser.close()
