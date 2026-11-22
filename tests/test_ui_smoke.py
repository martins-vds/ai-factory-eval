import pytest
from playwright.sync_api import sync_playwright


@pytest.mark.django_db
def test_loan_catalog_renders_in_browser(live_server):
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        try:
            page = browser.new_page()
            response = page.goto(f'{live_server.url}/ui/loans/', wait_until='commit')
            assert response is not None
            assert response.status == 200
            assert page.get_by_role('heading', name='Loan catalog').is_visible()
            assert page.get_by_text('9780134685991').is_visible()
            assert page.locator('a[href="/ui/loans/L1/"]').is_visible()
            assert page.locator('link[href="/static/css/tailwind.css"]').count() == 1
            assert page.locator(
                'script[src="https://cdn.jsdelivr.net/npm/htmx.org@2.0.11/dist/htmx.min.js"]'
            ).count() == 1
            page.locator('a[href="/ui/loans/L1/"]').click()
            assert page.get_by_role('heading', name='Loan L1').is_visible()
            missing = page.goto(f'{live_server.url}/ui/loans/missing/', wait_until='commit')
            assert missing is not None
            assert missing.status == 404
            assert page.get_by_role('heading', name='Loan not found').is_visible()
            admin = page.goto(f'{live_server.url}/admin/login/', wait_until='commit')
            assert admin is not None
            assert admin.status == 404
        finally:
            browser.close()
