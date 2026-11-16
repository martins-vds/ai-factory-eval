import logging

from django.http import HttpResponse
from django.utils import timezone
from django.utils.html import format_html
from django.shortcuts import render
from django.views.decorators.http import require_GET, require_POST

from src.loans.models import Loan

from .services import calculate_late_fee, pay_late_fee

logger = logging.getLogger(__name__)


def _fee_context(loan):
    through = loan.returned_on or timezone.localdate()
    days_late, amount = calculate_late_fee(loan.due_on, through)
    return {
        'loan': loan,
        'days_late': days_late,
        'fee': amount,
        'fee_display': f'{amount:.2f}',
    }


@require_GET
def fee_endpoint(request, loan_id):
    loan = Loan.objects.filter(pk=loan_id).first()
    if loan is None:
        return HttpResponse('<p>No such loan.</p>', status=404, content_type='text/html')

    context = _fee_context(loan)
    body = format_html(
        '<h1>Late fee for {}</h1><p>Due {}, {} day(s) late.</p><p class="fee">Fee: ${}</p>',
        context['loan'].id,
        loan.due_on.isoformat(),
        context['days_late'],
        context['fee_display'],
    )
    return HttpResponse(body, content_type='text/html')


@require_GET
def fee_page(request, loan_id):
    loan = Loan.objects.filter(pk=loan_id).first()
    if loan is None:
        return HttpResponse('<p>No such loan.</p>', status=404, content_type='text/html')
    return render(request, 'fees/page.html', _fee_context(loan))


@require_POST
def payment_endpoint(request, loan_id):
    if not Loan.objects.filter(pk=loan_id).exists():
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')
    result = pay_late_fee(loan_id)
    if result.interruption is not None:
        logger.error(
            'Payment gateway call interrupted (%s)',
            type(result.interruption).__name__,
        )
    return HttpResponse(result.body, status=result.status_code, content_type='text/plain')


@require_POST
def payment_page(request, loan_id):
    loan = Loan.objects.filter(pk=loan_id).first()
    if loan is None:
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')

    result = pay_late_fee(loan_id)
    if result.interruption is not None:
        logger.error(
            'Payment gateway call interrupted (%s)',
            type(result.interruption).__name__,
        )
    context = {**_fee_context(loan), 'payment_result': result}
    if request.headers.get('HX-Request') == 'true':
        return render(
            request,
            'fees/payment-result.html',
            context,
            status=result.status_code,
        )
    return render(request, 'fees/page.html', context, status=result.status_code)
