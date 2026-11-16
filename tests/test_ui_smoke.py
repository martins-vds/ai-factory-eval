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
            assert page.get_by_role('heading', name='The Lending Library').is_visible()
            assert page.get_by_text('Due 2026-01-16').is_visible()
            loan_link = page.get_by_role('link', name='View loan L1')
            assert loan_link.count() == 1, page.locator('body').inner_text()
            loan_link.click()
            assert page.get_by_role('heading', name='ana').is_visible()
            assert page.get_by_text('2026-01-16', exact=True).is_visible()
            assert page.request.get(f'{live_server.url}/admin/').status == 404
        finally:
            browser.close()
