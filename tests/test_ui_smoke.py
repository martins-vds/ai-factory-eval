import pytest
from playwright.sync_api import sync_playwright


@pytest.mark.django_db
def test_loan_catalog_ui_renders_in_browser(live_server):
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        try:
            page = browser.new_page()
            response = page.goto(f'{live_server.url}/ui/loans/')
            assert response is not None
            assert response.status == 200
            assert page.locator('h1').filter(has_text='Books in good company').is_visible()
            assert page.get_by_text('L1', exact=True).is_visible()
        finally:
            browser.close()
