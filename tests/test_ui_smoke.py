import pytest
from playwright.sync_api import sync_playwright


@pytest.mark.django_db
def test_loan_catalog_renders_in_browser(live_server):
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        try:
            page = browser.new_page()
            page.route('https://**', lambda route: route.abort())
            response = page.goto(f'{live_server.url}/ui/loans/', wait_until='domcontentloaded')
            assert response is not None
            assert response.status == 200
            assert page.get_by_role('heading', name='Books in good company.').is_visible()
            assert page.get_by_role('link', name='View loan L1').is_visible()
            assert (
                page.locator(
                    'link[href="https://cdn.jsdelivr.net/npm/daisyui@4.12.24/dist/full.min.css"]'
                ).count()
                == 1
            )
            assert page.locator('link[href="/static/css/tailwind.css"]').count() == 1
            assert (
                page.locator(
                    'script[src="https://cdn.jsdelivr.net/npm/htmx.org@2.0.11/dist/htmx.min.js"]'
                ).count()
                == 1
            )
        finally:
            browser.close()
