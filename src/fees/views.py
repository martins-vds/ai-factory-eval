from django.http import HttpResponse
from django.shortcuts import render
from django.utils.html import format_html
from django.views.decorators.http import require_GET, require_POST

from .composition import fee_application
from .gateway import PaymentGatewayUnavailable
from .services import PaymentResult


def fee_body(quote):
    amount = f'${quote.amount_cents // 100}.{quote.amount_cents % 100:02d}'
    return format_html(
        '<h1>Late fee for {}</h1><p>Due {}, {} day(s) late.</p><p class="fee">Fee: {}</p>',
        quote.loan.id,
        quote.loan.due_on.isoformat(),
        quote.late_days,
        amount,
    )


@require_GET
def fee_detail(request, loan_id):
    quote = fee_application.quote(loan_id)
    if quote is None:
        return HttpResponse('<p>No such loan.</p>', status=404, content_type='text/html')
    return HttpResponse(fee_body(quote), content_type='text/html')


@require_GET
def fee_page(request, loan_id):
    quote = fee_application.quote(loan_id)
    loan = quote.loan if quote else None
    amount = (
        f'${quote.amount_cents // 100}.{quote.amount_cents % 100:02d}'
        if quote
        else None
    )
    return render(
        request,
        'fees/detail.html',
        {'quote': quote, 'loan': loan, 'amount': amount},
        status=200 if quote else 404,
    )


@require_POST
def payment(request, loan_id):
    try:
        result = fee_application.pay(loan_id)
    except PaymentGatewayUnavailable:
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
        result = fee_application.pay(loan_id)
    except PaymentGatewayUnavailable:
        result = PaymentResult(502, b'payment gateway unavailable\n')

    succeeded = result is not None and result.status_code == 200
    message = (
        result.body.decode('utf-8', errors='replace').strip()
        if result
        else 'No such loan.'
    )
    is_htmx = request.headers.get('HX-Request') == 'true'
    status_code = (200 if is_htmx else 200 if succeeded else 502) if result else (
        200 if is_htmx else 404
    )
    template = 'fees/payment-status.html' if is_htmx else 'fees/payment-result.html'
    return render(
        request,
        template,
        {'loan_id': loan_id, 'succeeded': succeeded, 'message': message},
        status=status_code,
    )
