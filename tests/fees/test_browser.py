import pytest
from playwright.sync_api import sync_playwright


@pytest.mark.django_db
def test_htmx_payment_failure_is_rendered_in_the_fee_page(live_server, payment_gateway):
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        try:
            page = browser.new_page()
            response = page.goto(f'{live_server.url}/ui/fees/L2/')
            assert response is not None
            assert response.status == 200
            assert page.get_by_role('heading', name='Late fees').is_visible()

            page.get_by_role('button', name='Pay late fee').click()

            assert page.get_by_role('alert').get_by_text('Payment failed: declined').is_visible()
        finally:
            browser.close()
