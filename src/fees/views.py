import logging

from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.utils.html import format_html
from django.views.decorators.http import require_GET, require_POST

from .composition import fee_application, payment_application
from .services import PaymentGatewayUnavailable, PaymentResult

logger = logging.getLogger(__name__)


def _fee_context(fee):
    return {
        'fee': fee,
        'amount': f'{fee.amount_cents // 100}.{fee.amount_cents % 100:02d}',
    }


def _payment_result(loan_id):
    try:
        return payment_application.pay(loan_id)
    except PaymentGatewayUnavailable as error:
        logger.warning('Payment gateway call failed', exc_info=error)
        return PaymentResult(502, 'payment gateway unavailable\n')


@require_GET
def fee_api(request, loan_id):
    fee = fee_application.calculate(loan_id)
    if fee is None:
        return HttpResponse('<p>No such loan.</p>', status=404, content_type='text/html')

    body = format_html(
        '<h1>Late fee for {}</h1><p>Due {}, {} day(s) late.</p><p class="fee">Fee: ${}</p>',
        fee.loan_id,
        fee.due_on.isoformat(),
        fee.days_late,
        _fee_context(fee)['amount'],
    )
    return HttpResponse(body, content_type='text/html')


@require_GET
def fee_page(request, loan_id):
    fee = fee_application.calculate(loan_id)
    if fee is None:
        return render(request, 'fees/not-found.html', status=404)
    return render(request, 'fees/detail.html', _fee_context(fee))


@require_POST
def payment_api(request, loan_id):
    result = _payment_result(loan_id)
    return HttpResponse(result.body, status=result.status_code, content_type='text/plain')


@require_POST
def payment_page(request, loan_id):
    result = _payment_result(loan_id)

    if request.headers.get('HX-Request') == 'true':
        return render(
            request,
            'fees/payment-status.html',
            {
                'successful': result.status_code == 200,
                'not_found': result.status_code == 404,
            },
        )

    if result.status_code == 404:
        return render(request, 'fees/not-found.html', status=404)
    if result.status_code == 200:
        return redirect(f'/ui/fees/{loan_id}/')

    fee = fee_application.calculate(loan_id)
    if fee is None:
        return render(request, 'fees/not-found.html', status=404)
    return render(
        request,
        'fees/detail.html',
        {**_fee_context(fee), 'payment_error': True},
        status=502,
    )
