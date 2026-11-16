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
            assert page.get_by_role('heading', name='Books in good company.').is_visible()
            assert page.locator('main article').count() == 3
            assert page.get_by_text('With ana', exact=True).is_visible()
            assert page.locator('link[href*="daisyui@5.8.0"]').count() == 1
            assert (
                page.locator('script[src*="htmx.org"]')
                .get_attribute('src')
                .endswith('/htmx.org@2.0.11/dist/htmx.min.js')
            )
        finally:
            browser.close()
