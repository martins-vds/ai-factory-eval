import json
from pathlib import Path

from playwright.sync_api import sync_playwright

ABOUT_GOLDEN = json.loads(
    (
        Path(__file__).resolve().parents[2] / '.migration/characterization/source/goldens/http.json'
    ).read_text(encoding='utf-8')
)['GET /about']['response']


def test_about_endpoint_matches_characterized_response(client):
    response = client.get('/about')

    assert response.status_code == ABOUT_GOLDEN['status']
    assert response['Content-Type'] == ABOUT_GOLDEN['content_type']
    assert response.content.decode() == ABOUT_GOLDEN['body']


def test_about_pages_only_allow_get_requests(client):
    for path in ('/about', '/ui/about/'):
        assert client.post(path).status_code == 405


def test_about_page_presents_library_information_in_a_browser(live_server):
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        try:
            page = browser.new_page()
            response = page.goto(f'{live_server.url}/ui/about/')

            assert response is not None
            assert response.status == 200
            assert page.get_by_role('heading', name='About the Lending Library').is_visible()
            assert page.get_by_text('Monday to Saturday, 9:00 to 18:00', exact=False).is_visible()
            assert page.get_by_text('14-day lending period', exact=False).is_visible()
            assert page.locator('link[href="/static/css/tailwind.css"]').count() == 1
            assert page.locator('link[href*="daisyui@4.12.24"]').count() == 1
            assert page.locator('script[src*="htmx.org@2.0.11"]').count() == 1
            assert (
                page.get_by_role('link', name='desk@lending-library.invalid').get_attribute('href')
                == 'mailto:desk@lending-library.invalid'
            )
            assert (
                page.get_by_role('link', name='Browse the collection').get_attribute('href')
                == '/ui/loans/'
            )
        finally:
            browser.close()
