from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_GET, require_POST

from .composition import fee_application
from .services import PaymentGatewayFailure


def _fee_amount(amount_cents):
    return f'{amount_cents // 100}.{amount_cents % 100:02d}'


@require_GET
def fee_detail(request, loan_id):
    quote = fee_application.calculate_fee(loan_id)
    if quote is None:
        return HttpResponse('<p>No such loan.</p>', status=404, content_type='text/html')

    body = (
        f'<h1>Late fee for {quote.loan.id}</h1>'
        f'<p>Due {quote.loan.due_on.isoformat()}, {quote.days_late} day(s) late.</p>'
        f'<p class="fee">Fee: ${_fee_amount(quote.amount_cents)}</p>'
    )
    return HttpResponse(body, content_type='text/html')


@require_GET
def fee_page(request, loan_id):
    quote = fee_application.calculate_fee(loan_id)
    if quote is None:
        return render(
            request,
            'fees/fee.html',
            status=404,
        )
    return render(
        request,
        'fees/fee.html',
        {'quote': quote, 'fee_amount': _fee_amount(quote.amount_cents)},
    )


@require_POST
def payment_detail(request, loan_id):
    try:
        result = fee_application.pay(loan_id)
    except PaymentGatewayFailure:
        return HttpResponse(
            'payment gateway unavailable\n',
            status=502,
            content_type='text/plain',
        )

    if result is None:
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')
    return HttpResponse(result.body, status=result.status, content_type='text/plain')


@require_POST
def payment_page(request, loan_id):
    try:
        result = fee_application.pay(loan_id)
    except PaymentGatewayFailure:
        return _payment_error(request, loan_id, 'payment gateway unavailable', 502)

    if result is None:
        return _payment_error(request, loan_id, 'No such loan.', 404)

    if result.status == 200:
        if request.headers.get('HX-Request') != 'true':
            return redirect('fee_page', loan_id=loan_id)
        return render(
            request,
            'fees/payment-status.html',
            {'success': True, 'message': 'Payment accepted.', 'gateway_body': result.body},
        )
    return _payment_error(request, loan_id, result.body, result.status)


def _payment_error(request, loan_id, message, status):
    if request.headers.get('HX-Request') == 'true':
        return render(
            request,
            'fees/payment-status.html',
            {
                'loan_id': loan_id,
                'message': message,
            },
            status=status,
        )

    quote = fee_application.calculate_fee(loan_id)
    return render(
        request,
        'fees/fee.html',
        {
            'quote': quote,
            'fee_amount': _fee_amount(quote.amount_cents) if quote else None,
            'payment_error': message,
        },
        status=status,
    )
