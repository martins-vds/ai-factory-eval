import pytest
from playwright.sync_api import sync_playwright


@pytest.mark.django_db
def test_loan_catalog_renders_in_browser(live_server):
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        try:
            page = browser.new_page()
            response = page.goto(f'{live_server.url}/ui/loans/')
            assert response is not None
            assert response.status == 200
            assert page.get_by_role('heading', name='Loans in circulation').is_visible()
            assert page.get_by_text('ISBN 9780134685991', exact=True).is_visible()
            assert (
                page.locator(
                    'script[src="https://cdn.jsdelivr.net/npm/htmx.org@2.0.11/dist/htmx.min.js"]'
                ).count()
                == 1
            )
        finally:
            browser.close()
