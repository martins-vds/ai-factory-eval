import logging

from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone
from django.utils.html import format_html
from django.views.decorators.http import require_GET

from src.loans.repository import DjangoLoanRepository

from .gateway import GatewayResponse, PaymentGateway
from .services import calculate_late_fee

logger = logging.getLogger(__name__)
loan_repository = DjangoLoanRepository()
payment_gateway = PaymentGateway()


def fee_page_context(loan, payment_result=None):
    fee = calculate_late_fee(loan.due_on, loan.returned_on, timezone.localdate())
    return {
        'loan': loan,
        'fee': fee,
        'amount': f'${fee.amount_cents // 100}.{fee.amount_cents % 100:02d}',
        'payment_result': payment_result,
    }


def charge_loan_fee(loan_id):
    try:
        return payment_gateway.charge(loan_id)
    except InterruptedError:
        logger.exception('Payment gateway request interrupted')
        return GatewayResponse(502, 'payment gateway unavailable\n')


@require_GET
def fee_detail(request, loan_id):
    loan = loan_repository.find(loan_id)
    if loan is None:
        return HttpResponse('<p>No such loan.</p>', status=404, content_type='text/html')

    fee = calculate_late_fee(loan.due_on, loan.returned_on, timezone.localdate())
    return HttpResponse(
        format_html(
            '<h1>Late fee for {}</h1><p>Due {}, {} day(s) late.</p><p class="fee">Fee: ${}</p>',
            loan.id,
            loan.due_on.isoformat(),
            fee.days_late,
            f'{fee.amount_cents // 100}.{fee.amount_cents % 100:02d}',
        ),
        content_type='text/html',
    )


@require_GET
def fee_page(request, loan_id):
    loan = loan_repository.find(loan_id)
    if loan is None:
        return HttpResponse('<p>No such loan.</p>', status=404, content_type='text/html')

    return render(request, 'fees/detail.html', fee_page_context(loan))


def payment(request, loan_id):
    if loan_repository.find(loan_id) is None:
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')

    result = charge_loan_fee(loan_id)
    return HttpResponse(result.body, status=result.status_code, content_type='text/plain')


def payment_page(request, loan_id):
    loan = loan_repository.find(loan_id)
    if loan is None:
        return HttpResponse(
            '<p>No such loan.</p>',
            status=404,
            content_type='text/html',
        )

    result = charge_loan_fee(loan_id)
    context = fee_page_context(
        loan,
        {
            'succeeded': result.status_code == 200,
            'body': result.body,
        },
    )
    if request.headers.get('HX-Request') == 'true':
        return render(request, 'fees/payment-status.html', context)
    return render(request, 'fees/detail.html', context)
