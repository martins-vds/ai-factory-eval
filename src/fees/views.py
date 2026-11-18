import logging

from django.http import HttpResponse
from django.shortcuts import render
from django.utils.html import format_html
from django.views.decorators.http import require_GET, require_POST

from .composition import fee_application
from .gateway import PaymentInterrupted
from .services import PaymentResult

logger = logging.getLogger(__name__)


@require_GET
def fee_detail(request, loan_id):
    fee = fee_application.calculate(loan_id)
    if fee is None:
        return HttpResponse('<p>No such loan.</p>', status=404, content_type='text/html')

    content = format_html(
        '<h1>Late fee for {}</h1><p>Due {}, {} day(s) late.</p><p class="fee">Fee: ${}</p>',
        fee.loan.id,
        fee.loan.due_on.isoformat(),
        fee.days_late,
        format(fee.amount, '.2f'),
    )
    return HttpResponse(content, content_type='text/html')


@require_GET
def fee_page(request, loan_id):
    fee = fee_application.calculate(loan_id)
    if fee is None:
        return HttpResponse('<p>No such loan.</p>', status=404, content_type='text/html')
    return render(
        request,
        'fees/page.html',
        {'fee': fee, 'fees': fee_application.all_fees()},
    )


@require_POST
def payment(request, loan_id):
    result = _charge(loan_id)
    if result is None:
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')
    return HttpResponse(result.body, status=result.status, content_type='text/plain')


@require_POST
def payment_page(request, loan_id):
    fee = fee_application.calculate(loan_id)
    if fee is None:
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')

    result = _charge(loan_id)
    if result is None:
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')
    if request.headers.get('HX-Request') == 'true':
        return render(
            request,
            'fees/payment-status.html',
            {'result': result},
        )

    return render(
        request,
        'fees/page.html',
        {'fee': fee, 'fees': fee_application.all_fees(), 'result': result},
    )


def _charge(loan_id):
    try:
        return fee_application.pay(loan_id)
    except PaymentInterrupted:
        logger.exception('Payment gateway request was interrupted')
        return PaymentResult(502, 'payment gateway unavailable\n')
