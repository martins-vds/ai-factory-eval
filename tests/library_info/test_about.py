import pytest
from playwright.sync_api import sync_playwright


def test_about_response_preserves_the_characterized_html(client):
    response = client.get('/about')

    assert response.status_code == 200
    assert response['Content-Type'].partition(';')[0] == 'text/html'
    assert response.content == (
        b'<!doctype html>\n'
        b'<html lang="en">\n'
        b'<head><meta charset="utf-8"><title>About the Lending Library</title></head>\n'
        b'<body>\n'
        b'  <h1>About the Lending Library</h1>\n'
        b'  <p>Open Monday to Saturday, 9:00 to 18:00. Books are lent for 14 days.</p>\n'
        b'  <p>Contact: desk@lending-library.invalid</p>\n'
        b'</body>\n'
        b'</html>\n'
    )


@pytest.mark.django_db
def test_modern_about_page_presents_library_information_in_the_browser(live_server):
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
