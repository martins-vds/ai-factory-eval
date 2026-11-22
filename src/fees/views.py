import logging

from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET, require_POST

from .composition import fee_application, payment_application
from .gateway import PaymentGatewayUnavailable
from .services import PaymentResponse

logger = logging.getLogger(__name__)


@require_GET
def fee_detail(request, loan_id):
    fee = fee_application.calculate(loan_id)
    if fee is None:
        return HttpResponse('<p>No such loan.</p>', status=404, content_type='text/html')

    loan = fee.loan
    amount = f'${fee.amount_cents // 100}.{fee.amount_cents % 100:02d}'
    body = (
        f'<h1>Late fee for {loan.id}</h1>'
        f'<p>Due {loan.due_on.isoformat()}, {fee.days_late} day(s) late.</p>'
        f'<p class="fee">Fee: {amount}</p>'
    )
    return HttpResponse(body, content_type='text/html')


@require_GET
def fee_page(request, loan_id):
    fee = fee_application.calculate(loan_id)
    if fee is None:
        return HttpResponse('<p>No such loan.</p>', status=404, content_type='text/html')
    return render(
        request,
        'fees/fee-page.html',
        {
            'fee': fee,
            'loan': fee.loan,
            'amount': f'${fee.amount_cents // 100}.{fee.amount_cents % 100:02d}',
        },
    )


@require_POST
def payment(request, loan_id):
    response = _charge(loan_id)
    if response is None:
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')
    return HttpResponse(response.body, status=response.status, content_type='text/plain')


@require_POST
def fee_payment(request, loan_id):
    response = _charge(loan_id)
    if response is None:
        if request.headers.get('HX-Request') == 'true':
            return render(
                request,
                'fees/payment-result.html',
                {'payment': PaymentResponse(404, 'no such loan\n')},
            )
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')

    fee = fee_application.calculate(loan_id)
    if fee is None:
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')

    context = {
        'fee': fee,
        'loan': fee.loan,
        'amount': f'${fee.amount_cents // 100}.{fee.amount_cents % 100:02d}',
        'payment': response,
    }
    if request.headers.get('HX-Request') == 'true':
        return render(request, 'fees/payment-result.html', context)
    return render(request, 'fees/fee-page.html', context)


def _charge(loan_id):
    try:
        return payment_application.pay(loan_id)
    except PaymentGatewayUnavailable:
        logger.exception('Payment gateway request failed')
        return PaymentResponse(502, 'payment gateway unavailable\n')
