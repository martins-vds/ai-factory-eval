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
            assert page.get_by_role('heading', name='The loan catalog').is_visible()
            assert page.locator('link[href*="css/tailwind.css"]').count() == 1
            assert page.locator('script[src*="htmx.org@2.0.11"]').count() == 1
            page.get_by_role('link', name='View record L1').click()
            assert page.get_by_role('heading', name='Loan L1').is_visible()
        finally:
            browser.close()
