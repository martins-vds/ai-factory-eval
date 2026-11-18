from playwright.sync_api import sync_playwright

LEGACY_ABOUT_HTML = """<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><title>About the Lending Library</title></head>
<body>
  <h1>About the Lending Library</h1>
  <p>Open Monday to Saturday, 9:00 to 18:00. Books are lent for 14 days.</p>
  <p>Contact: desk@lending-library.invalid</p>
</body>
</html>
"""


def test_legacy_about_response_is_unchanged(client):
    response = client.get('/about')

    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'text/html'
    assert response.content.decode() == LEGACY_ABOUT_HTML


def test_about_pages_only_allow_get(client):
    assert client.post('/about').status_code == 405
    assert client.post('/ui/about/').status_code == 405


def test_about_page_renders_reading_room_information_in_browser(live_server):
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
            contact = page.get_by_role('link', name='desk@lending-library.invalid')
            assert contact.is_visible()
            assert contact.get_attribute('href') == 'mailto:desk@lending-library.invalid'
        finally:
            browser.close()
