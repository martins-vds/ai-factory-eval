from datetime import date

import pytest
from playwright.sync_api import sync_playwright

from src.loans.models import Loan


@pytest.mark.django_db
def test_browser_displays_gateway_failure_from_htmx_payment(
    monkeypatch, live_server, payment_gateway
):
    Loan.objects.create(
        id='L-ui',
        member='dee',
        isbn='123',
        lent_on=date(2025, 12, 1),
        returned_on=date(2026, 1, 3),
    )
    payment_gateway.status = 503
    payment_gateway.body = b'declined\n'
    monkeypatch.setenv('PAYMENT_GATEWAY_URL', payment_gateway.url)

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        try:
            page = browser.new_page()
            page.goto(f'{live_server.url}/ui/fees/L-ui/')
            page.get_by_role('button', name='Pay late fee').click()
            status = page.locator('#payment-status')
            status.get_by_role('alert').wait_for()
            assert 'declined' in status.inner_text()
        finally:
            browser.close()
