from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET, require_POST

from .composition import fee_application, payment_application
from .services import GatewayResponse, PaymentFailed


def fee_amount(amount_cents):
    return f'${amount_cents // 100}.{amount_cents % 100:02d}'


def fee_context(fee):
    return {
        'fee': fee,
        'late_days': fee.quote.late_days,
        'amount': fee_amount(fee.quote.amount_cents),
    }


@require_GET
def fee_api(request, loan_id):
    fee = fee_application.quote(loan_id)
    if fee is None:
        return HttpResponse('<p>No such loan.</p>', status=404, content_type='text/html')

    return HttpResponse(
        f'<h1>Late fee for {fee.loan.id}</h1>'
        f'<p>Due {fee.loan.due_on.isoformat()}, {fee.quote.late_days} day(s) late.</p>'
        f'<p class="fee">Fee: {fee_amount(fee.quote.amount_cents)}</p>',
        content_type='text/html',
    )


@require_GET
def fee_page(request, loan_id):
    fee = fee_application.quote(loan_id)
    if fee is None:
        return render(request, 'fees/not-found.html', status=404)
    return render(request, 'fees/page.html', fee_context(fee))


@require_POST
def payment_api(request, loan_id):
    try:
        result = payment_application.pay(loan_id)
    except PaymentFailed as error:
        return HttpResponse(error.body, status=502, content_type='text/plain')

    if result is None:
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')
    return HttpResponse(result.body, status=result.status, content_type='text/plain')


@require_POST
def payment_page(request, loan_id):
    try:
        result = payment_application.pay(loan_id)
    except PaymentFailed as error:
        result = GatewayResponse(status=502, body=error.body)

    if result is None:
        if request.headers.get('HX-Request') == 'true':
            return render(
                request,
                'fees/payment-result.html',
                {'payment_status': 404, 'message': 'No such loan.'},
                status=404,
            )
        return render(request, 'fees/not-found.html', status=404)

    message = result.body.decode('utf-8', errors='replace').strip()
    context = {
        'payment_status': result.status,
        'message': message or 'Payment could not be completed.',
    }
    if request.headers.get('HX-Request') == 'true':
        return render(
            request,
            'fees/payment-result.html',
            context,
            status=result.status,
        )

    fee = fee_application.quote(loan_id)
    return render(
        request,
        'fees/page.html',
        {**fee_context(fee), **context},
        status=result.status,
    )
