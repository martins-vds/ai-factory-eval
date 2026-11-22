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
            assert page.get_by_role('link', name='Loan L1').is_visible()
            assert page.get_by_text('ana · ISBN 9780134685991').is_visible()
            page.get_by_role('link', name='Loan L1').click()
            assert page.get_by_role('heading', name='A book in good company.').is_visible()
        finally:
            browser.close()
