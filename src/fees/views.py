import logging

from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone
from django.utils.html import format_html
from django.views.decorators.http import require_GET, require_POST

from src.loans.models import Loan

from .gateway import PaymentGatewayFailure, charge_loan
from .services import calculate_late_fee

logger = logging.getLogger(__name__)


def _late_fee_context(loan):
    days_late, amount_cents = calculate_late_fee(
        loan.due_on,
        loan.returned_on,
        timezone.localdate(),
    )
    return {
        'loan': loan,
        'days_late': days_late,
        'amount_cents': amount_cents,
        'amount': f'{amount_cents // 100}.{amount_cents % 100:02d}',
    }


def _log_interruption(error):
    if isinstance(error.__cause__, InterruptedError):
        logger.warning(
            'Payment gateway request was interrupted: %s: %s',
            type(error.__cause__).__name__,
            error.__cause__,
        )


@require_GET
def fee_api(request, loan_id):
    loan = Loan.objects.filter(pk=loan_id).first()
    if loan is None:
        return HttpResponse(
            '<p>No such loan.</p>',
            status=404,
            content_type='text/html',
        )

    fee = _late_fee_context(loan)
    body = format_html(
        '<h1>Late fee for {}</h1><p>Due {}, {} day(s) late.</p><p class="fee">Fee: ${}</p>',
        loan.id,
        loan.due_on.isoformat(),
        fee['days_late'],
        fee['amount'],
    )
    return HttpResponse(body, content_type='text/html')


@require_GET
def fee_page(request, loan_id):
    loan = Loan.objects.filter(pk=loan_id).first()
    if loan is None:
        return HttpResponse('<p>No such loan.</p>', status=404, content_type='text/html')
    return render(request, 'fees/fee.html', _late_fee_context(loan))


@require_POST
def payment_api(request, loan_id):
    if not Loan.objects.filter(pk=loan_id).exists():
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')

    try:
        status, body = charge_loan(loan_id)
    except PaymentGatewayFailure as error:
        _log_interruption(error)
        return HttpResponse(
            str(error),
            status=502,
            content_type='text/plain',
        )
    return HttpResponse(
        body,
        status=200 if status == 200 else 502,
        content_type='text/plain',
    )


@require_POST
def payment_page(request, loan_id):
    loan = Loan.objects.filter(pk=loan_id).first()
    if loan is None:
        return HttpResponse('<p>No such loan.</p>', status=404, content_type='text/html')

    try:
        status, body = charge_loan(loan_id)
        success = status == 200
        message = body.decode('utf-8')
    except PaymentGatewayFailure as error:
        _log_interruption(error)
        success = False
        message = str(error)

    template = (
        'fees/payment-status.html'
        if request.headers.get('HX-Request') == 'true'
        else 'fees/payment-result.html'
    )
    return render(request, template, {'loan': loan, 'success': success, 'message': message})
