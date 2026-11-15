import logging

from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET, require_POST

from src.loans.models import Loan

from .gateway import PaymentInterrupted, charge_loan_fee
from .services import calculate_late_fee

logger = logging.getLogger(__name__)


def _not_found():
    return HttpResponse('<p>No such loan.</p>', status=404, content_type='text/html')


def _payment_response(loan_id):
    try:
        return charge_loan_fee(loan_id)
    except PaymentInterrupted:
        logger.exception('Payment gateway request was interrupted')
        return 502, 'payment gateway unavailable\n'


def _fee_page(request, loan, payment_result=None):
    fee = calculate_late_fee(loan)
    return render(
        request,
        'fees/fee.html',
        {'fee': fee, 'loan': loan, 'payment_result': payment_result},
    )


@require_GET
def fee_api(request, loan_id):
    loan = Loan.objects.filter(pk=loan_id).first()
    if loan is None:
        return _not_found()

    fee = calculate_late_fee(loan)
    body = (
        f'<h1>Late fee for {loan.id}</h1>'
        f'<p>Due {loan.due_on.isoformat()}, {fee.days_late} day(s) late.</p>'
        f'<p class="fee">Fee: {fee.formatted_amount}</p>'
    )
    return HttpResponse(body, content_type='text/html')


@require_POST
def payment_api(request, loan_id):
    if not Loan.objects.filter(pk=loan_id).exists():
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')

    status, body = _payment_response(loan_id)
    return HttpResponse(body, status=200 if status == 200 else 502, content_type='text/plain')


@require_GET
def fee_page(request, loan_id):
    loan = Loan.objects.filter(pk=loan_id).first()
    if loan is None:
        return _not_found()
    return _fee_page(request, loan)


@require_POST
def payment_page(request, loan_id):
    loan = Loan.objects.filter(pk=loan_id).first()
    if loan is None:
        return _not_found()

    status, _ = _payment_response(loan_id)
    payment_result = {'success': status == 200}
    if request.headers.get('HX-Request') == 'true':
        return render(request, 'fees/payment-status.html', {'payment_result': payment_result})
    return _fee_page(request, loan, payment_result)
