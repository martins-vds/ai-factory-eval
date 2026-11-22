from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_GET, require_POST

from .composition import fee_application, payment_application
from .services import GatewayUnavailable, LoanNotFound


def _fee_context(quote):
    return {
        'quote': quote,
        'fee': f'${quote.fee_cents // 100}.{quote.fee_cents % 100:02d}',
    }


def _is_htmx(request):
    return request.headers.get('HX-Request') == 'true'


@require_GET
def fee_api(request, loan_id):
    quote = fee_application.calculate(loan_id)
    if quote is None:
        return HttpResponse('<p>No such loan.</p>', status=404, content_type='text/html')

    body = (
        f'<h1>Late fee for {quote.loan.id}</h1>'
        f'<p>Due {quote.loan.due_on.isoformat()}, {quote.days_late} day(s) late.</p>'
        f'<p class="fee">Fee: ${quote.fee_cents // 100}.{quote.fee_cents % 100:02d}</p>'
    )
    return HttpResponse(body, content_type='text/html')


@require_POST
def payment_api(request, loan_id):
    try:
        result = payment_application.pay(loan_id)
    except LoanNotFound:
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')
    except GatewayUnavailable:
        return HttpResponse(
            'payment gateway unavailable\n',
            status=502,
            content_type='text/plain',
        )

    return HttpResponse(result.body, status=result.status, content_type='text/plain')


@require_GET
def fee_page(request, loan_id):
    quote = fee_application.calculate(loan_id)
    if quote is None:
        return render(request, 'fees/not-found.html', status=404)
    return render(request, 'fees/fee.html', _fee_context(quote))


@require_POST
def payment_page(request, loan_id):
    htmx_request = _is_htmx(request)
    try:
        result = payment_application.pay(loan_id)
    except LoanNotFound:
        if htmx_request:
            return render(
                request,
                'fees/payment-status.html',
                {'error': True, 'message': 'No such loan.'},
                status=404,
            )
        return render(request, 'fees/not-found.html', status=404)
    except GatewayUnavailable:
        return _payment_failure(
            request,
            loan_id,
            'payment gateway unavailable',
            htmx_request,
        )

    if result.status != 200:
        return _payment_failure(
            request,
            loan_id,
            result.body.decode(errors='replace').strip(),
            htmx_request,
        )
    if htmx_request:
        return render(
            request,
            'fees/payment-status.html',
            {'error': False, 'message': 'Payment complete.'},
        )
    return redirect(f'/ui/fees/{loan_id}/')


def _payment_failure(request, loan_id, message, htmx_request):
    if htmx_request:
        return render(
            request,
            'fees/payment-status.html',
            {'error': True, 'message': message},
            status=502,
        )

    quote = fee_application.calculate(loan_id)
    if quote is None:
        return render(request, 'fees/not-found.html', status=404)
    return render(
        request,
        'fees/fee.html',
        {**_fee_context(quote), 'payment_error': message},
        status=502,
    )
