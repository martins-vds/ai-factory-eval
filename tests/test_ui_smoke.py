import pytest
from playwright.sync_api import sync_playwright


@pytest.mark.django_db
def test_loan_catalog_and_detail_render_in_browser(live_server):
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        try:
            page = browser.new_page()
            response = page.goto(f'{live_server.url}/ui/loans/')
            assert response is not None
            assert response.status == 200
            assert page.locator('link[href*="tailwind.css"]').count() == 1
            assert (
                page.locator(
                    'script[src="https://cdn.jsdelivr.net/npm/htmx.org@2.0.11/dist/htmx.min.js"]'
                ).count()
                == 1
            )
            assert page.get_by_role('heading', name='The reading room').is_visible()
            assert page.get_by_text('Borrowed by ana', exact=True).is_visible()
            page.get_by_role('link', name='L1').click()
            assert page.get_by_text('Loan L1', exact=True).is_visible()
            assert page.get_by_role('heading', name='9780134685991').is_visible()
        finally:
            browser.close()
