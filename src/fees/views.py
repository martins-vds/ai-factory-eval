import logging

from django.http import HttpResponse
from django.shortcuts import render
from django.utils.html import escape
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from .composition import fee_application, payment_application
from .gateway import GatewayUnavailable

logger = logging.getLogger(__name__)


@require_GET
def fee_detail(request, loan_id):
    result = fee_application.get(loan_id)
    if result is None:
        return HttpResponse(
            '<p>No such loan.</p>',
            status=404,
            content_type='text/html',
        )

    loan, fee = result
    body = (
        f'<h1>Late fee for {escape(loan.id)}</h1>'
        f'<p>Due {loan.due_on.isoformat()}, {fee.late_days} day(s) late.</p>'
        f'<p class="fee">Fee: {fee.amount}</p>'
    )
    return HttpResponse(body, content_type='text/html')


@require_GET
def fee_page(request, loan_id):
    result = fee_application.get(loan_id)
    if result is None:
        return HttpResponse(
            '<p>No such loan.</p>',
            status=404,
            content_type='text/html',
        )

    loan, fee = result
    return render(request, 'fees/detail.html', _fee_page_context(loan, fee))


@csrf_exempt
@require_POST
def payment(request, loan_id):
    try:
        result = payment_application.pay(loan_id)
    except GatewayUnavailable:
        logger.exception('Payment gateway request failed')
        return HttpResponse(
            'payment gateway unavailable\n',
            status=502,
            content_type='text/plain',
        )
    if result is None:
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')
    return HttpResponse(result.body, status=result.status, content_type='text/plain')


@require_POST
def fee_payment(request, loan_id):
    try:
        result = payment_application.pay(loan_id)
        message = result.body if result is not None else 'no such loan\n'
        successful = result is not None and result.status == 200
    except GatewayUnavailable:
        logger.exception('Payment gateway request failed')
        result = None
        message = 'payment gateway unavailable\n'
        successful = False

    if result is None and not successful and message == 'no such loan\n':
        return HttpResponse(message, status=404, content_type='text/plain')

    response_context = {'body': message, 'successful': successful}
    if request.headers.get('HX-Request') == 'true':
        return render(request, 'fees/payment-result.html', response_context)

    fee_result = fee_application.get(loan_id)
    if fee_result is None:
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')
    loan, fee = fee_result
    context = _fee_page_context(loan, fee)
    context['payment_result'] = response_context
    return render(request, 'fees/detail.html', context)


def _fee_page_context(loan, fee):
    fees = [{'loan': item_loan, 'fee': item_fee} for item_loan, item_fee in fee_application.all()]
    return {'loan': loan, 'fee': fee, 'fees': fees}
