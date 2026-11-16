import json
from pathlib import Path

from playwright.sync_api import sync_playwright

HTTP_GOLDENS = json.loads(
    (
        Path(__file__).resolve().parents[2] / '.migration/characterization/source/goldens/http.json'
    ).read_text(encoding='utf-8')
)


def test_about_endpoint_matches_characterized_response(client):
    response = client.get('/about')
    expected = HTTP_GOLDENS['GET /about']['response']

    assert response.status_code == expected['status']
    assert response['Content-Type'] == expected['content_type']
    assert response.content.decode() == expected['body']


def test_about_ui_presents_reading_room_information(client):
    response = client.get('/ui/about/')

    assert response.status_code == 200
    assert b'A place for curious readers' in response.content
    assert (
        b'A neighborhood collection, kept in motion by the people who read it.' in response.content
    )
    assert b'Open Monday to Saturday, 9:00 to 18:00.' in response.content
    assert b'Books are lent for 14 days.' in response.content
    assert b'href="mailto:desk@lending-library.invalid"' in response.content
    assert b'href="/ui/loans/"' in response.content


def test_about_ui_is_usable_in_a_browser(live_server):
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        try:
            page = browser.new_page()
            response = page.goto(f'{live_server.url}/ui/about/')

            assert response is not None
            assert response.status == 200
            assert page.get_by_role('heading', name='About the Lending Library').is_visible()
            assert page.get_by_text('Open Monday to Saturday, 9:00 to 18:00.').is_visible()
            assert (
                page.get_by_role('link', name='desk@lending-library.invalid').get_attribute('href')
                == 'mailto:desk@lending-library.invalid'
            )
        finally:
            browser.close()
