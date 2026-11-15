import pytest
from playwright.sync_api import sync_playwright


@pytest.mark.django_db(transaction=True)
def test_reading_room_can_lend_and_return_a_book(live_server):
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        try:
            page = browser.new_page()
            page.goto(f'{live_server.url}/ui/loans/')
            assert page.get_by_role('heading', name='Books in good company.').is_visible()
            page.get_by_label('Member').fill('reader')
            page.get_by_label('ISBN').fill('9780000000001')
            page.get_by_role('button', name='Record loan').click()

            loan = page.locator('#loan-L4')
            assert loan.get_by_text('reader · ISBN 9780000000001').is_visible()
            assert loan.get_by_text('On loan').is_visible()
            loan.get_by_role('button', name='Mark returned').click()
            assert loan.get_by_text('Returned', exact=False).is_visible()
            assert loan.get_by_role('button', name='Mark returned').count() == 0
        finally:
            browser.close()
