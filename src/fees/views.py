import logging

from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.views.decorators.http import require_GET, require_POST

from src.loans.models import Loan

from .gateway import PaymentGatewayError, charge_loan
from .services import calculate_late_fee

logger = logging.getLogger(__name__)


def _fee_context(loan):
    fee = calculate_late_fee(loan)
    return {
        'loan': loan,
        'days_late': fee.days_late,
        'amount': f'{fee.amount_cents // 100}.{fee.amount_cents % 100:02d}',
        'fee_due': fee.days_late > 2,
    }


@require_GET
def fee_api(request, loan_id):
    loan = Loan.objects.filter(pk=loan_id).first()
    if loan is None:
        response = HttpResponse('<p>No such loan.</p>', status=404)
    else:
        body = render_to_string('fees/api.html', _fee_context(loan), request=request).removesuffix(
            '\n'
        )
        response = HttpResponse(body)
    response['Content-Type'] = 'text/html'
    return response


@require_POST
def payment_api(request, loan_id):
    if not Loan.objects.filter(pk=loan_id).exists():
        return _plain_text('no such loan\n', status=404)
    payment = _charge_loan(loan_id)
    if payment is None:
        return _plain_text('payment gateway unavailable\n', status=502)
    gateway_status, body = payment
    return _plain_text(body, status=200 if gateway_status == 200 else 502)


@require_GET
def fee_page(request, loan_id):
    loan = Loan.objects.filter(pk=loan_id).first()
    if loan is None:
        return HttpResponse('<p>No such loan.</p>', status=404)
    return render(request, 'fees/detail.html', _fee_context(loan))


@require_POST
def payment_page(request, loan_id):
    loan = Loan.objects.filter(pk=loan_id).first()
    if loan is None:
        return _plain_text('no such loan\n', status=404)
    payment = _charge_loan(loan_id)
    if payment is None:
        return _plain_text('payment gateway unavailable\n', status=502)
    gateway_status, body = payment
    if gateway_status != 200:
        return _plain_text(body, status=502)
    if request.headers.get('HX-Request') != 'true':
        return redirect(f'/ui/fees/{loan_id}/')
    return render(request, 'fees/payment-status.html', {'loan': loan})


def _charge_loan(loan_id):
    try:
        return charge_loan(loan_id)
    except PaymentGatewayError as error:
        if isinstance(error.__cause__, InterruptedError):
            logger.warning('Payment gateway call interrupted', exc_info=error)
        return None


def _plain_text(body, status):
    response = HttpResponse(body, status=status)
    response['Content-Type'] = 'text/plain'
    return response
