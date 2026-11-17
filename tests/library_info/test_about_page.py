import pytest
from playwright.sync_api import sync_playwright


def test_about_endpoint_matches_characterized_response(client):
    response = client.get('/about')

    assert response.status_code == 200
    assert response['Content-Type'].split(';', maxsplit=1)[0] == 'text/html'
    assert response.content.decode() == (
        '<!doctype html>\n'
        '<html lang="en">\n'
        '<head><meta charset="utf-8"><title>About the Lending Library</title></head>\n'
        '<body>\n'
        '  <h1>About the Lending Library</h1>\n'
        '  <p>Open Monday to Saturday, 9:00 to 18:00. Books are lent for 14 days.</p>\n'
        '  <p>Contact: desk@lending-library.invalid</p>\n'
        '</body>\n'
        '</html>\n'
    )


@pytest.mark.django_db
def test_about_page_displays_library_information_in_the_reading_room(live_server):
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        try:
            page = browser.new_page(viewport={'width': 390, 'height': 844})
            response = page.goto(f'{live_server.url}/ui/about/')

            assert response is not None
            assert response.status == 200
            assert page.get_by_role('heading', name='About the Lending Library').is_visible()
            assert page.get_by_text('Monday—Saturday').is_visible()
            assert page.get_by_text('09:00 — 18:00').is_visible()
            assert page.get_by_text('14 days', exact=True).is_visible()
            assert page.get_by_role('link', name='desk@lending-library.invalid').get_attribute(
                'href'
            ) == 'mailto:desk@lending-library.invalid'
            assert page.get_by_role('link', name='Browse the collection').get_attribute(
                'href'
            ) == '/ui/loans/'
        finally:
            browser.close()
