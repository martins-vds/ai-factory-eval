import logging

from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET, require_POST

from .composition import fee_application, payment_application
from .gateway import GatewayResponse, GatewayUnavailable

logger = logging.getLogger(__name__)


def _not_found():
    return HttpResponse('no such loan\n', status=404, content_type='text/plain')


def _payment_result(loan_id):
    try:
        return payment_application.pay(loan_id)
    except GatewayUnavailable:
        logger.exception('Payment gateway request failed')
        return GatewayResponse(502, 'payment gateway unavailable\n')


@require_GET
def fee_endpoint(request, loan_id):
    fee_data = fee_application.get_fee(loan_id)
    if fee_data is None:
        return HttpResponse('<p>No such loan.</p>', status=404, content_type='text/html')

    loan, fee = fee_data
    body = (
        f'<h1>Late fee for {loan.id}</h1>'
        f'<p>Due {loan.due_on.isoformat()}, {fee.days_late} day(s) late.</p>'
        f'<p class="fee">Fee: {fee.amount}</p>'
    )
    return HttpResponse(body, content_type='text/html')


@require_GET
def fee_page(request, loan_id):
    fee_data = fee_application.get_fee(loan_id)
    if fee_data is None:
        return _not_found()

    loan, fee = fee_data
    return render(request, 'fees/page.html', {'loan': loan, 'fee': fee})


@require_POST
def payment_endpoint(request, loan_id):
    result = _payment_result(loan_id)
    if result is None:
        return _not_found()
    status = 200 if result.status_code == 200 else 502
    return HttpResponse(result.body, status=status, content_type='text/plain')


@require_POST
def payment_page(request, loan_id):
    result = _payment_result(loan_id)
    if result is None:
        return _not_found()

    fee_data = fee_application.get_fee(loan_id)
    if fee_data is None:
        return _not_found()

    loan, fee = fee_data
    context = {
        'loan': loan,
        'fee': fee,
        'payment_result': result,
    }
    if request.headers.get('HX-Request') == 'true':
        return render(request, 'fees/payment-status.html', context)
    return render(request, 'fees/page.html', context)
