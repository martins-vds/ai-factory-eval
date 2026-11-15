import json
from pathlib import Path

from playwright.sync_api import sync_playwright

ABOUT_GOLDEN_PATH = (
    Path(__file__).resolve().parents[2] / '.migration/characterization/source/goldens/http.json'
)
ABOUT_GOLDEN = json.loads(ABOUT_GOLDEN_PATH.read_text(encoding='utf-8'))['GET /about']['response']


def test_about_endpoint_matches_characterized_html(client):
    response = client.get('/about')

    assert response.status_code == ABOUT_GOLDEN['status']
    assert response['Content-Type'] == ABOUT_GOLDEN['content_type']
    assert response.content.decode() == ABOUT_GOLDEN['body']


def test_about_page_presents_reading_room_information_in_a_browser(live_server):
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        try:
            page = browser.new_page()
            response = page.goto(f'{live_server.url}/ui/about/')

            assert response is not None
            assert response.status == 200
            assert page.get_by_role('heading', name='About the Lending Library').is_visible()
            assert page.get_by_text('A neighborhood collection, kept in motion by the people who read it.').is_visible()
            assert page.get_by_text('Open Monday to Saturday, 9:00 to 18:00.').is_visible()
            assert page.get_by_text('Books are lent for 14 days.').is_visible()
            assert page.get_by_role('link', name='desk@lending-library.invalid').get_attribute('href') == (
                'mailto:desk@lending-library.invalid'
            )
        finally:
            browser.close()
