import logging

from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET, require_POST

from .composition import fee_application, payment_application
from .services import (
    LoanNotFound,
    PaymentGatewayInterrupted,
    PaymentResult,
)

logger = logging.getLogger(__name__)


def _fee_amount(amount_cents):
    return f'${amount_cents // 100}.{amount_cents % 100:02d}'


@require_GET
def fee_detail(request, loan_id):
    try:
        fee = fee_application.fee_for(loan_id)
    except LoanNotFound:
        return HttpResponse('<p>No such loan.</p>', status=404, content_type='text/html')

    body = (
        f'<h1>Late fee for {fee.loan.id}</h1>'
        f'<p>Due {fee.loan.due_on.isoformat()}, {fee.days_late} day(s) late.</p>'
        f'<p class="fee">Fee: {_fee_amount(fee.amount_cents)}</p>'
    )
    return HttpResponse(body, content_type='text/html')


@require_GET
def fee_page(request, loan_id):
    try:
        fee = fee_application.fee_for(loan_id)
    except LoanNotFound:
        return HttpResponse('<p>No such loan.</p>', status=404, content_type='text/html')

    return render(
        request,
        'fees/detail.html',
        {
            'fee': fee,
            'amount': _fee_amount(fee.amount_cents),
        },
    )


def _pay(loan_id):
    try:
        return payment_application.pay(loan_id)
    except LoanNotFound:
        return PaymentResult(404, 'no such loan\n')
    except PaymentGatewayInterrupted:
        logger.exception('payment gateway request interrupted')
        return PaymentResult(502, 'payment gateway unavailable\n')


@require_POST
def pay(request, loan_id):
    result = _pay(loan_id)
    return HttpResponse(result.body, status=result.status_code, content_type='text/plain')


@require_POST
def pay_page(request, loan_id):
    result = _pay(loan_id)
    return render(
        request,
        'fees/payment-result.html',
        {
            'body': result.body,
            'success': result.status_code == 200,
        },
        status=result.status_code,
    )
