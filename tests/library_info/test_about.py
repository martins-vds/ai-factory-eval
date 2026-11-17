import json
from pathlib import Path

import pytest
from playwright.sync_api import sync_playwright

HTTP_GOLDENS = json.loads(
    (
        Path(__file__).resolve().parents[2] / '.migration/characterization/source/goldens/http.json'
    ).read_text(encoding='utf-8')
)


def test_about_endpoint_matches_characterized_response(client):
    expected = HTTP_GOLDENS['GET /about']['response']

    response = client.get('/about')

    assert response.status_code == expected['status']
    assert response['Content-Type'] == expected['content_type']
    assert response.content.decode() == expected['body']


@pytest.mark.parametrize('path', ['/about', '/ui/about/'])
def test_about_pages_only_accept_get(client, path):
    response = client.post(path)

    assert response.status_code == 405


def test_about_page_presents_library_information_in_the_browser(live_server):
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        try:
            page = browser.new_page()
            response = page.goto(f'{live_server.url}/ui/about/')

            assert response is not None
            assert response.status == 200
            assert page.get_by_role('heading', name='About the Lending Library').is_visible()
            assert page.get_by_text(
                'A neighborhood collection, kept in motion by the people who read it.'
            ).is_visible()
            assert page.get_by_text('Open Monday to Saturday, 9:00 to 18:00.').is_visible()
            assert page.get_by_text('Books are lent for 14 days.').is_visible()
            assert (
                page.get_by_role('link', name='desk@lending-library.invalid').get_attribute('href')
                == 'mailto:desk@lending-library.invalid'
            )
        finally:
            browser.close()
