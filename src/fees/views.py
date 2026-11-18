import logging

from django.http import HttpResponse
from django.shortcuts import render
from django.utils.html import format_html
from django.views.decorators.http import require_GET, require_POST

from .composition import fee_application, payment_application

logger = logging.getLogger(__name__)


def _log_payment_failure(loan_id, result):
    if result.failure is None:
        return

    error = result.failure
    logger.warning(
        'Payment gateway request failed for loan %s',
        loan_id,
        exc_info=(type(error), error, error.__traceback__),
    )


@require_GET
def fee_detail(request, loan_id):
    fee = fee_application.calculate(loan_id)
    if fee is None:
        return HttpResponse('<p>No such loan.</p>', status=404, content_type='text/html')

    return HttpResponse(
        format_html(
            '<h1>Late fee for {}</h1><p>Due {}, {} day(s) late.</p><p class="fee">Fee: ${}</p>',
            fee.loan_id,
            fee.due_on.isoformat(),
            fee.late_days,
            fee.formatted_amount,
        ),
        content_type='text/html',
    )


@require_GET
def fee_page(request, loan_id):
    fee = fee_application.calculate(loan_id)
    if fee is None:
        return HttpResponse('<p>No such loan.</p>', status=404, content_type='text/html')

    return render(request, 'fees/fee-detail.html', {'fee': fee})


@require_POST
def payment_detail(request, loan_id):
    result = payment_application.charge(loan_id)
    _log_payment_failure(loan_id, result)
    return HttpResponse(result.body, status=result.status, content_type='text/plain')


@require_POST
def payment_page(request, loan_id):
    result = payment_application.charge(loan_id)
    _log_payment_failure(loan_id, result)
    template = (
        'fees/payment-status.html'
        if request.headers.get('HX-Request') == 'true'
        else 'fees/payment-result.html'
    )
    return render(request, template, {'loan_id': loan_id, 'result': result}, status=result.status)
