from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET, require_POST

from .composition import fee_application, payment_application
from .gateway import PaymentGatewayUnavailable


@require_GET
def late_fee(request, loan_id):
    quote = fee_application.quote(loan_id)
    if quote is None:
        return HttpResponse('<p>No such loan.</p>', status=404, content_type='text/html')

    body = (
        f'<h1>Late fee for {quote.loan.id}</h1>'
        f'<p>Due {quote.loan.due_on.isoformat()}, {quote.days_late} day(s) late.</p>'
        f'<p class="fee">Fee: {quote.formatted_amount}</p>'
    )
    return HttpResponse(body, content_type='text/html')


@require_GET
def late_fee_page(request, loan_id):
    quote = fee_application.quote(loan_id)
    if quote is None:
        return HttpResponse('<p>No such loan.</p>', status=404, content_type='text/html')
    return render(
        request,
        'fees/late-fee.html',
        {'loan': quote.loan, 'days_late': quote.days_late, 'fee': quote.formatted_amount},
    )


@require_POST
def pay_fee(request, loan_id):
    try:
        payment = payment_application.pay(loan_id)
    except PaymentGatewayUnavailable:
        return HttpResponse(
            'payment gateway unavailable\n',
            status=502,
            content_type='text/plain',
        )
    if payment is None:
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')
    return HttpResponse(payment.body, status=payment.status_code, content_type='text/plain')


@require_POST
def pay_fee_page(request, loan_id):
    try:
        payment = payment_application.pay(loan_id)
    except PaymentGatewayUnavailable:
        return render(
            request,
            'fees/payment-status.html',
            {'successful': False, 'message': 'Payment gateway unavailable.'},
        )
    if payment is None:
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')
    return render(
        request,
        'fees/payment-status.html',
        {
            'successful': payment.status_code == 200,
            'message': payment.body.strip(),
        },
    )
