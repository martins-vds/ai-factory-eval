import pytest
from playwright.sync_api import sync_playwright


@pytest.mark.django_db
def test_loan_catalog_page_renders_in_browser(live_server):
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        try:
            page = browser.new_page()
            response = page.goto(f'{live_server.url}/ui/loans/')
            assert response is not None
            assert response.status == 200
            assert page.get_by_role('heading', name='Books in good company.').is_visible()
            assert page.get_by_text('9780134685991').is_visible()
            body_classes = (page.locator('body').get_attribute('class') or '').split()
            assert 'variant-reading-room' in body_classes
            stylesheet = page.locator('link[rel="stylesheet"]').get_attribute('href')
            assert stylesheet == '/static/css/tailwind.css'
            assert page.locator('script[src*="htmx.org@2.0.11"]').count() == 1
        finally:
            browser.close()
