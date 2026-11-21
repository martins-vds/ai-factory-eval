import json
from pathlib import Path

import pytest
from playwright.sync_api import sync_playwright


HTTP_GOLDEN_PATH = (
    Path(__file__).resolve().parents[2]
    / '.migration/characterization/source/goldens/http.json'
)


@pytest.mark.django_db
def test_about_endpoint_preserves_characterized_response(client):
    expected = json.loads(HTTP_GOLDEN_PATH.read_text(encoding='utf-8'))['GET /about'][
        'response'
    ]

    response = client.get('/about')

    assert response.status_code == expected['status']
    assert response['Content-Type'] == expected['content_type']
    assert response.content.decode() == expected['body']


@pytest.mark.django_db
def test_browser_about_page_shows_library_information(client):
    response = client.get('/ui/about/')

    assert response.status_code == 200
    assert b'About the Lending Library' in response.content
    assert b'Open Monday to Saturday, 9:00 to 18:00.' in response.content
    assert b'Books are lent for 14 days.' in response.content
    assert b'href="mailto:desk@lending-library.invalid"' in response.content


@pytest.mark.django_db
def test_about_page_is_readable_in_a_mobile_browser(live_server):
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        try:
            page = browser.new_page(viewport={'width': 390, 'height': 844})
            response = page.goto(f'{live_server.url}/ui/about/')

            assert response is not None
            assert response.status == 200
            assert page.get_by_role('heading', name='About the Lending Library').is_visible()
            assert page.get_by_role('link', name='desk@lending-library.invalid').is_visible()
            assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth')
        finally:
            browser.close()
