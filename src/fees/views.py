import logging

from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone
from django.utils.html import format_html
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from src.loans.models import Loan

from .gateway import GatewayResponse, HttpPaymentGateway, PaymentGatewayUnavailable
from .services import calculate_late_fee

logger = logging.getLogger(__name__)


def _late_fee(loan):
    return calculate_late_fee(loan, today=timezone.localdate())


@require_GET
def fee_api(request, loan_id):
    loan = Loan.objects.filter(pk=loan_id).first()
    if loan is None:
        return HttpResponse('<p>No such loan.</p>', status=404, content_type='text/html')

    fee = _late_fee(loan)
    body = format_html(
        '<h1>Late fee for {}</h1><p>Due {}, {} day(s) late.</p><p class="fee">Fee: {}</p>',
        loan.id,
        loan.due_on.isoformat(),
        fee.late_days,
        fee.amount,
    )
    return HttpResponse(body, content_type='text/html')


def _fee_page_context(loan, payment_status=None):
    return {
        'loan': loan,
        'fee': _late_fee(loan),
        'payment_status': payment_status,
    }


@require_GET
def fee_page(request, loan_id):
    loan = Loan.objects.filter(pk=loan_id).first()
    if loan is None:
        return render(request, 'fees/not-found.html', status=404)
    return render(request, 'fees/detail.html', _fee_page_context(loan))


def _charge(loan_id):
    try:
        response = HttpPaymentGateway().charge(loan_id)
    except PaymentGatewayUnavailable:
        logger.exception('Payment gateway request failed')
        return GatewayResponse(502, 'payment gateway unavailable\n')
    return GatewayResponse(
        status_code=200 if response.status_code == 200 else 502,
        body=response.body,
    )


@require_POST
@csrf_exempt
def payment_api(request, loan_id):
    if not Loan.objects.filter(pk=loan_id).exists():
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')

    response = _charge(loan_id)
    return HttpResponse(response.body, status=response.status_code, content_type='text/plain')


@require_POST
def payment_page(request, loan_id):
    loan = Loan.objects.filter(pk=loan_id).first()
    if loan is None:
        if request.headers.get('HX-Request') == 'true':
            return render(
                request,
                'fees/payment-status.html',
                {'success': False, 'message': 'No such loan.'},
                status=404,
            )
        return render(request, 'fees/not-found.html', status=404)

    response = _charge(loan_id)
    success = response.status_code == 200
    message = (
        f'Payment received for {loan_id}.'
        if success
        else response.body.strip() or 'Payment could not be completed.'
    )
    if request.headers.get('HX-Request') == 'true':
        return render(
            request,
            'fees/payment-status.html',
            {'success': success, 'message': message},
        )

    payment_status = {'success': success, 'message': message}
    return render(
        request,
        'fees/detail.html',
        _fee_page_context(loan, payment_status),
        status=response.status_code,
    )
