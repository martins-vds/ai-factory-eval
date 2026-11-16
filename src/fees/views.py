import logging

from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.utils.html import format_html
from django.views.decorators.http import require_GET, require_POST

from src.loans.models import Loan

from .gateway import (
    PaymentGatewayInterrupted,
    PaymentGatewayUnavailable,
    charge_loan,
)
from .services import calculate_late_fee

logger = logging.getLogger(__name__)


@require_GET
def late_fee(request, loan_id):
    loan = Loan.objects.filter(pk=loan_id).first()
    if loan is None:
        return HttpResponse('<p>No such loan.</p>', status=404, content_type='text/html')

    fee = calculate_late_fee(loan)
    body = format_html(
        '<h1>Late fee for {}</h1><p>Due {}, {} day(s) late.</p><p class="fee">Fee: ${}</p>',
        loan.id,
        fee.due_on.isoformat(),
        fee.days_late,
        format(fee.amount, '.2f'),
    )
    return HttpResponse(body, content_type='text/html')


@require_POST
def payment(request, loan_id):
    if not Loan.objects.filter(pk=loan_id).exists():
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')

    try:
        result = charge_loan(loan_id)
    except PaymentGatewayInterrupted:
        logger.exception('Payment gateway request was interrupted')
        return HttpResponse(
            'payment gateway unavailable\n',
            status=502,
            content_type='text/plain',
        )
    except PaymentGatewayUnavailable:
        return HttpResponse(
            'payment gateway unavailable\n',
            status=502,
            content_type='text/plain',
        )
    return HttpResponse(
        result.body,
        status=result.status_code,
        content_type='text/plain',
    )


@require_GET
def late_fee_page(request, loan_id):
    loan = Loan.objects.filter(pk=loan_id).first()
    if loan is None:
        return HttpResponse('<p>No such loan.</p>', status=404, content_type='text/html')

    return render(
        request,
        'fees/page.html',
        {'loan': loan, 'fee': calculate_late_fee(loan)},
    )


@require_POST
def payment_page(request, loan_id):
    loan = Loan.objects.filter(pk=loan_id).first()
    if loan is None:
        return HttpResponse('<p>No such loan.</p>', status=404, content_type='text/html')

    try:
        result = charge_loan(loan_id)
    except PaymentGatewayInterrupted:
        logger.exception('Payment gateway request was interrupted')
        result = None
    except PaymentGatewayUnavailable:
        result = None

    succeeded = result is not None and result.status_code == 200
    message = (
        result.body.decode('utf-8', errors='replace').strip()
        if result is not None
        else 'payment gateway unavailable'
    )
    if request.headers.get('HX-Request') == 'true':
        return render(
            request,
            'fees/payment-status.html',
            {'succeeded': succeeded, 'message': message},
        )
    if succeeded:
        return redirect(f'/ui/fees/{loan.id}/')
    return render(
        request,
        'fees/page.html',
        {
            'loan': loan,
            'fee': calculate_late_fee(loan),
            'payment_status': {'succeeded': False, 'message': message},
        },
    )
