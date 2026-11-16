import logging

from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.html import format_html
from django.views.decorators.http import require_GET, require_POST

from src.loans.models import Loan

from .composition import payment_application
from .payments import GatewayResponse, PaymentGatewayUnavailable
from .services import calculate_late_fee

logger = logging.getLogger(__name__)


def _fee_page_context(loan, payment_error=None):
    fee = calculate_late_fee(loan, timezone.localdate())
    context = {
        'loan': loan,
        'fee': fee,
        'fee_amount': f'${fee.cents // 100}.{fee.cents % 100:02d}',
    }
    if payment_error is not None:
        context['payment_error'] = payment_error
    return context


def _payment_result(loan_id):
    try:
        return payment_application.pay(loan_id)
    except PaymentGatewayUnavailable:
        logger.exception('Payment gateway unavailable for loan %s', loan_id)
        return GatewayResponse(status_code=502, body='payment gateway unavailable\n')


@require_GET
def fee_detail(request, loan_id):
    loan = Loan.objects.filter(pk=loan_id).first()
    if loan is None:
        return HttpResponse('<p>No such loan.</p>', status=404, content_type='text/html')

    fee = calculate_late_fee(loan, timezone.localdate())
    amount = f'{fee.cents // 100}.{fee.cents % 100:02d}'
    body = format_html(
        '<h1>Late fee for {}</h1><p>Due {}, {} day(s) late.</p><p class="fee">Fee: ${}</p>',
        loan.id,
        loan.due_on.isoformat(),
        fee.days_late,
        amount,
    )
    return HttpResponse(body, content_type='text/html')


@require_GET
def fee_page(request, loan_id):
    loan = Loan.objects.filter(pk=loan_id).first()
    if loan is None:
        return HttpResponse('<p>No such loan.</p>', status=404, content_type='text/html')

    return render(request, 'fees/detail.html', _fee_page_context(loan))


@require_POST
def payment(request, loan_id):
    result = _payment_result(loan_id)
    if result is None:
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')
    return HttpResponse(result.body, status=result.status_code, content_type='text/plain')


@require_POST
def payment_page(request, loan_id):
    result = _payment_result(loan_id)
    if result is None:
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')

    if result.status_code == 200 and request.headers.get('HX-Request') != 'true':
        return redirect(reverse('fee_page', kwargs={'loan_id': loan_id}))

    if request.headers.get('HX-Request') == 'true':
        return render(
            request,
            'fees/payment-status.html',
            {'result': result},
        )

    loan = Loan.objects.get(pk=loan_id)
    return render(
        request,
        'fees/detail.html',
        _fee_page_context(loan, payment_error=result.body),
        status=result.status_code,
    )
