import pytest
from playwright.sync_api import sync_playwright


@pytest.mark.django_db
def test_about_page_displays_library_information_in_browser(live_server):
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        try:
            page = browser.new_page()
            response = page.goto(f'{live_server.url}/ui/about/')

            assert response is not None
            assert response.status == 200
            assert page.get_by_role('heading', name='About the Lending Library').is_visible()
            assert page.get_by_text('Open Monday to Saturday, 9:00 to 18:00.').is_visible()
            assert page.get_by_text('Books are lent for 14 days.').is_visible()
            assert page.get_by_role(
                'link', name='desk@lending-library.invalid'
            ).get_attribute('href') == 'mailto:desk@lending-library.invalid'
        finally:
            browser.close()
