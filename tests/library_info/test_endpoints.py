import json
from pathlib import Path

from playwright.sync_api import sync_playwright

HTTP_GOLDEN_PATH = (
    Path(__file__).resolve().parents[2] / '.migration/characterization/source/goldens/http.json'
)
HTTP_GOLDENS = json.loads(HTTP_GOLDEN_PATH.read_text(encoding='utf-8'))


def test_about_endpoint_matches_characterized_html(client):
    expected = HTTP_GOLDENS['GET /about']['response']

    response = client.get('/about')

    assert response.status_code == expected['status']
    assert response['Content-Type'] == expected['content_type']
    assert response.content.decode() == expected['body']


def test_about_page_only_allows_get(client):
    response = client.post('/about')

    assert response.status_code == 405


def test_about_ui_uses_the_library_information_template_and_assets(client):
    response = client.get('/ui/about/')

    assert response.status_code == 200
    assert response.templates[0].name == 'library_info/about.html'
    assert b'A place for curious readers' in response.content
    assert b'About the Lending Library' in response.content
    assert b'Open Monday to Saturday, 9:00 to 18:00.' in response.content
    assert b'Books are lent for 14 days.' in response.content
    assert b'href="mailto:desk@lending-library.invalid"' in response.content
    assert b'daisyui@4.12.24' in response.content
    assert b'/static/css/tailwind.css' in response.content
    assert b'htmx.org@2.0.11' in response.content


def test_about_ui_renders_in_a_browser(live_server):
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        try:
            page = browser.new_page()
            response = page.goto(f'{live_server.url}/ui/about/')

            assert response is not None
            assert response.status == 200
            assert page.get_by_role('heading', name='About the Lending Library').is_visible()
            assert page.get_by_text('Open Monday to Saturday, 9:00 to 18:00.').is_visible()
            assert page.get_by_role('link', name='desk@lending-library.invalid').get_attribute(
                'href'
            ) == 'mailto:desk@lending-library.invalid'
        finally:
            browser.close()
