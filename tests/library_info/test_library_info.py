import json
from pathlib import Path

from playwright.sync_api import sync_playwright

HTTP_GOLDEN_PATH = (
    Path(__file__).resolve().parents[2] / '.migration/characterization/source/goldens/http.json'
)
ABOUT_GOLDEN = json.loads(HTTP_GOLDEN_PATH.read_text(encoding='utf-8'))['GET /about']['response']


def test_about_http_endpoint_matches_characterized_html(client):
    response = client.get('/about')

    assert response.status_code == ABOUT_GOLDEN['status']
    assert response['Content-Type'] == ABOUT_GOLDEN['content_type']
    assert response.content.decode() == ABOUT_GOLDEN['body']


def test_about_routes_reject_non_get_requests(client):
    for path in ('/about', '/ui/about/'):
        assert client.post(path).status_code == 405


def test_about_page_shows_library_information(client):
    response = client.get('/ui/about/')

    assert response.status_code == 200
    assert b'A place for curious readers' in response.content
    assert b'Open Monday to Saturday, 9:00 to 18:00.' in response.content
    assert b'Books are lent for 14 days.' in response.content
    assert b'href="mailto:desk@lending-library.invalid"' in response.content
    assert b'href="/ui/loans/"' in response.content


def test_about_page_is_readable_in_a_browser(live_server):
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
        finally:
            browser.close()
