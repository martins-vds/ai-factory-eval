import pytest
from playwright.sync_api import sync_playwright


@pytest.mark.django_db
def test_loan_catalog_renders_in_browser(live_server):
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        try:
            page = browser.new_page()
            response = page.goto(f'{live_server.url}/ui/loans/', wait_until='domcontentloaded')
            assert response is not None
            assert response.status == 200
            assert page.get_by_role('heading', name='Stories on loan').is_visible()
            assert page.get_by_role('link', name='L1').get_attribute('href') == '/ui/loans/L1/'
            assert page.get_by_role('cell', name='ana').is_visible()
        finally:
            browser.close()
