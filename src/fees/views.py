import logging

from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.utils.html import format_html
from django.views.decorators.http import require_GET, require_POST

from .composition import fee_application
from .services import PaymentGatewayInterrupted

logger = logging.getLogger(__name__)


@require_GET
def late_fee(request, loan_id):
    fee = fee_application.fee(loan_id)
    if fee is None:
        return HttpResponse('<p>No such loan.</p>', status=404, content_type='text/html')

    body = format_html(
        '<h1>Late fee for {}</h1><p>Due {}, {} day(s) late.</p><p class="fee">Fee: ${}</p>',
        fee.loan_id,
        fee.due_on.isoformat(),
        fee.days_late,
        format(fee.amount, '.2f'),
    )
    return HttpResponse(body, content_type='text/html')


@require_POST
def payment(request, loan_id):
    result = fee_application.pay(loan_id)
    if result is None:
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')

    _log_interruption(result)
    return HttpResponse(
        result.body,
        status=result.status_code,
        content_type='text/plain',
    )


@require_GET
def late_fee_page(request, loan_id):
    fee = fee_application.fee(loan_id)
    if fee is None:
        return HttpResponse('<p>No such loan.</p>', status=404, content_type='text/html')

    return render(request, 'fees/page.html', {'fee': fee})


@require_POST
def payment_page(request, loan_id):
    result = fee_application.pay(loan_id)
    if result is None:
        return HttpResponse('<p>No such loan.</p>', status=404, content_type='text/html')

    _log_interruption(result)
    succeeded = result.status_code == 200
    message = result.body.decode('utf-8', errors='replace').strip()
    if request.headers.get('HX-Request') == 'true':
        return render(
            request,
            'fees/payment-status.html',
            {'succeeded': succeeded, 'message': message},
        )
    if succeeded:
        return redirect(f'/ui/fees/{loan_id}/')
    fee = fee_application.fee(loan_id)
    return render(
        request,
        'fees/page.html',
        {
            'fee': fee,
            'payment_status': {'succeeded': False, 'message': message},
        },
    )


def _log_interruption(result):
    failure = result.failure
    if isinstance(failure, PaymentGatewayInterrupted):
        logger.error(
            'Payment gateway request was interrupted',
            exc_info=(type(failure), failure, failure.__traceback__),
        )
