import logging
from urllib.parse import urlencode

from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from src.loans.models import Loan

from .gateway import PaymentGatewayUnavailable, charge_loan
from .services import calculate_late_fee

logger = logging.getLogger(__name__)


def fee_detail(request, loan_id):
    loan = Loan.objects.filter(pk=loan_id).first()
    if loan is None:
        return HttpResponse('<p>No such loan.</p>', status=404, content_type='text/html')

    fee = calculate_late_fee(loan.due_on, loan.returned_on, timezone.localdate())
    return HttpResponse(
        f'<h1>Late fee for {loan.id}</h1><p>Due {loan.due_on.isoformat()}, '
        f'{fee.days_late} day(s) late.</p><p class="fee">Fee: ${fee.amount:.2f}</p>',
        content_type='text/html',
    )


def fee_page(request, loan_id):
    loan = Loan.objects.filter(pk=loan_id).first()
    if loan is None:
        return HttpResponse('<p>No such loan.</p>', status=404, content_type='text/html')

    fee = calculate_late_fee(loan.due_on, loan.returned_on, timezone.localdate())
    return render(
        request,
        'fees/detail.html',
        {
            'loan': loan,
            'fee': fee,
            'payment_success': request.GET.get('payment') == 'success',
            'payment_error': request.GET.get('payment') == 'failed',
        },
    )


def _payment_result(loan_id):
    try:
        status, body = charge_loan(loan_id)
    except PaymentGatewayUnavailable as error:
        if isinstance(error.__cause__, InterruptedError):
            logger.warning('Payment gateway call interrupted', exc_info=error)
        return 502, b'payment gateway unavailable\n'

    return (200 if status == 200 else 502), body


@require_POST
def payment_detail(request, loan_id):
    if not Loan.objects.filter(pk=loan_id).exists():
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')

    status, body = _payment_result(loan_id)

    return HttpResponse(
        body.decode('utf-8', errors='replace'),
        status=status,
        content_type='text/plain',
    )


@require_POST
def payment_page(request, loan_id):
    if not Loan.objects.filter(pk=loan_id).exists():
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')

    status, body = _payment_result(loan_id)
    succeeded = status == 200
    if request.headers.get('HX-Request') == 'true':
        return render(
            request,
            'fees/payment-result.html',
            {'success': succeeded, 'detail': body.decode('utf-8', errors='replace')},
        )
    fee_url = reverse('fee-page', kwargs={'loan_id': loan_id})
    payment_status = 'success' if succeeded else 'failed'
    return redirect(f'{fee_url}?{urlencode({"payment": payment_status})}')
