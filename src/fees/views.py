from django.http import HttpResponse
from django.shortcuts import render
from django.utils.html import format_html
from django.views.decorators.http import require_GET, require_POST

from .composition import fee_application, payment_application
from .services import PaymentGatewayError


@require_GET
def fee_api(request, loan_id):
    fee = fee_application.calculate_fee(loan_id)
    if fee is None:
        return HttpResponse('<p>No such loan.</p>', status=404, content_type='text/html')

    amount = f'{fee.fee_cents // 100}.{fee.fee_cents % 100:02d}'
    body = format_html(
        '<h1>Late fee for {}</h1><p>Due {}, {} day(s) late.</p><p class="fee">Fee: ${}</p>',
        fee.loan.id,
        fee.loan.due_on.isoformat(),
        fee.days_late,
        amount,
    )
    return HttpResponse(body, content_type='text/html')


@require_GET
def fee_page(request, loan_id):
    fee = fee_application.calculate_fee(loan_id)
    if fee is None:
        return HttpResponse('<p>No such loan.</p>', status=404, content_type='text/html')

    return render(
        request,
        'fees/detail.html',
        {
            'fee': fee,
            'fee_amount': f'{fee.fee_cents // 100}.{fee.fee_cents % 100:02d}',
        },
    )


@require_POST
def payment_api(request, loan_id):
    try:
        result = payment_application.pay(loan_id)
    except PaymentGatewayError:
        return HttpResponse(
            'payment gateway unavailable\n',
            status=502,
            content_type='text/plain',
        )
    if result is None:
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')
    return HttpResponse(result.body, status=result.status_code, content_type='text/plain')


@require_POST
def payment_page(request, loan_id):
    try:
        result = payment_application.pay(loan_id)
    except PaymentGatewayError:
        return render(
            request,
            'fees/payment-status.html',
            {'message': 'Payment gateway unavailable.', 'successful': False},
            status=502,
        )
    if result is None:
        return render(
            request,
            'fees/payment-status.html',
            {'message': 'No such loan.', 'successful': False},
            status=404,
        )
    return render(
        request,
        'fees/payment-status.html',
        {'message': result.body, 'successful': result.status_code == 200},
        status=result.status_code,
    )
