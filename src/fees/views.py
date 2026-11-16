import logging

from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST

from src.loans.models import Loan

from .gateway import (
    GatewayResponse,
    PaymentGatewayFailure,
    PaymentGatewayInterrupted,
    charge_loan,
)
from .services import calculate_late_fee

logger = logging.getLogger(__name__)


def _find_loan(loan_id):
    return Loan.objects.filter(pk=loan_id).first()


def fee_detail(request, loan_id):
    loan = _find_loan(loan_id)
    if loan is None:
        return HttpResponse('<p>No such loan.</p>', status=404, content_type='text/html')

    fee = calculate_late_fee(loan)
    return HttpResponse(
        f'<h1>Late fee for {loan.id}</h1>'
        f'<p>Due {loan.due_on.isoformat()}, {fee.days_late} day(s) late.</p>'
        f'<p class="fee">Fee: ${fee.amount:.2f}</p>',
        content_type='text/html',
    )


def fee_page(request, loan_id):
    loan = _find_loan(loan_id)
    if loan is None:
        return HttpResponse('<p>No such loan.</p>', status=404, content_type='text/html')

    return render(
        request,
        'fees/detail.html',
        {'loan': loan, 'fee': calculate_late_fee(loan)},
    )


@require_POST
def payment_api(request, loan_id):
    if _find_loan(loan_id) is None:
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')

    result = _charge_payment(loan_id)
    return HttpResponse(result.body, status=result.status_code, content_type='text/plain')


def _charge_payment(loan_id):
    try:
        return charge_loan(loan_id)
    except PaymentGatewayInterrupted:
        logger.exception('Payment gateway request was interrupted')
    except PaymentGatewayFailure:
        pass

    return GatewayResponse(502, b'payment gateway unavailable\n')


@require_POST
def payment_page(request, loan_id):
    loan = _find_loan(loan_id)
    if loan is None:
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')

    result = _charge_payment(loan_id)
    context = {
        'loan': loan,
        'successful': result.status_code == 200,
        'message': result.body.decode('utf-8', errors='replace').strip(),
    }
    if request.headers.get('HX-Request') == 'true':
        return render(request, 'fees/payment-status.html', context)

    status_code = 200 if context['successful'] else 502
    return render(request, 'fees/payment-result.html', context, status=status_code)
