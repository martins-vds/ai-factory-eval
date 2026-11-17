import pytest
from playwright.sync_api import sync_playwright


def test_about_endpoint_matches_characterized_response(client):
    response = client.get('/about')

    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'text/html'
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
def test_about_ui_renders_reading_room_content_and_assets(client, live_server):
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        try:
            page = browser.new_page()
            response = page.goto(f'{live_server.url}/ui/about/')

            assert response is not None
            assert response.status == 200
            assert page.get_by_role('heading', name='About the Lending Library').is_visible()
            assert page.get_by_text(
                'Open Monday to Saturday, 9:00 to 18:00. Books are lent for 14 days.',
                exact=True,
            ).is_visible()
            assert page.get_by_text('Contact: desk@lending-library.invalid', exact=True).is_visible()
            assert page.locator('link[href="/static/css/tailwind.css"]').count() == 1
            assert (
                page.locator(
                    'link[href="https://cdn.jsdelivr.net/npm/daisyui@4.12.24/dist/full.min.css"]'
                ).count()
                == 1
            )
            assert (
                page.locator(
                    'script[src="https://cdn.jsdelivr.net/npm/htmx.org@2.0.11/dist/htmx.min.js"]'
                ).count()
                == 1
            )
        finally:
            browser.close()
