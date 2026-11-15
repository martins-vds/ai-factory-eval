import logging

from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST

from src.loans.models import Loan

from .gateway import PaymentGateway, PaymentGatewayFailure, PaymentGatewayInterrupted
from .services import calculate_late_fee

logger = logging.getLogger(__name__)
payment_gateway = PaymentGateway()


def _fee_details(loan):
    fee = calculate_late_fee(
        due_on=loan.due_on,
        returned_on=loan.returned_on,
        today=timezone.localdate(),
    )
    amount = f'${fee.amount_cents // 100}.{fee.amount_cents % 100:02d}'
    return {'loan': loan, 'fee': fee, 'amount': amount}


@require_GET
def fee_api(request, loan_id):
    loan = Loan.objects.filter(pk=loan_id).first()
    if loan is None:
        return HttpResponse('<p>No such loan.</p>', status=404, content_type='text/html')

    details = _fee_details(loan)
    fee = details['fee']
    body = (
        f'<h1>Late fee for {loan.id}</h1>'
        f'<p>Due {loan.due_on.isoformat()}, {fee.days_late} day(s) late.</p>'
        f'<p class="fee">Fee: {details["amount"]}</p>'
    )
    return HttpResponse(body, content_type='text/html')


@require_GET
def fee_page(request, loan_id):
    loan = Loan.objects.filter(pk=loan_id).first()
    if loan is None:
        return HttpResponse('<p>No such loan.</p>', status=404, content_type='text/html')
    return render(request, 'fees/page.html', _fee_details(loan))


def _payment_result(loan_id):
    if not Loan.objects.filter(pk=loan_id).exists():
        return 404, b'no such loan\n'
    try:
        status, body = payment_gateway.charge(loan_id)
    except PaymentGatewayInterrupted:
        logger.warning('Payment gateway call interrupted', exc_info=True)
        return 502, b'payment gateway unavailable\n'
    except PaymentGatewayFailure:
        return 502, b'payment gateway unavailable\n'
    return (200 if status == 200 else 502), body


@require_POST
def payment_api(request, loan_id):
    status, body = _payment_result(loan_id)
    return HttpResponse(body, status=status, content_type='text/plain')


@require_POST
def payment_page(request, loan_id):
    status, body = _payment_result(loan_id)
    if status == 404:
        return render(
            request,
            'fees/payment-result.html',
            {'success': False, 'message': 'No such loan.'},
        )
    message = body.decode('utf-8', errors='replace').strip()
    return render(
        request,
        'fees/payment-result.html',
        {
            'success': status == 200,
            'message': message or ('Payment received.' if status == 200 else 'Payment failed.'),
        },
    )
