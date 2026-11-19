import json
from pathlib import Path

import pytest
from playwright.sync_api import sync_playwright


def test_legacy_about_response_matches_characterization(client):
    golden_path = (
        Path(__file__).parents[2]
        / '.migration'
        / 'characterization'
        / 'source'
        / 'goldens'
        / 'http.json'
    )
    expected = json.loads(golden_path.read_text())['GET /about']['response']

    response = client.get('/about')

    assert response.status_code == expected['status']
    assert response['Content-Type'] == f"{expected['content_type']}; charset=utf-8"
    assert response.content.decode() == expected['body']


@pytest.mark.django_db
def test_about_page_renders_in_browser_with_reading_room_information(live_server):
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        try:
            page = browser.new_page()
            response = page.goto(
                f'{live_server.url}/ui/about/',
                wait_until='domcontentloaded',
            )
            assert response is not None
            assert response.status == 200
            assert page.get_by_role('heading', name='About the Lending Library').is_visible()
            assert page.get_by_text(
                'A neighborhood collection, kept in motion by the people who read it.'
            ).is_visible()
            assert page.get_by_text('Open Monday to Saturday, 9:00 to 18:00.').is_visible()
            assert page.get_by_text('Books are lent for 14 days.').is_visible()
            contact = page.get_by_role('link', name='desk@lending-library.invalid')
            assert contact.is_visible()
            assert contact.get_attribute('href') == 'mailto:desk@lending-library.invalid'
        finally:
            browser.close()
