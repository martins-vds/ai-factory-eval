import logging

from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_GET, require_POST

from .composition import fee_application, payment_application
from .gateway import GatewayFailure

logger = logging.getLogger(__name__)


@require_GET
def fee_api(request, loan_id):
    quote = fee_application.quote(loan_id)
    if quote is None:
        response = HttpResponse('<p>No such loan.</p>', status=404, content_type='text/html')
    else:
        amount = f'{quote.amount_cents // 100}.{quote.amount_cents % 100:02d}'
        body = (
            f'<h1>Late fee for {quote.loan.id}</h1>'
            f'<p>Due {quote.loan.due_on.isoformat()}, {quote.days_late} day(s) late.</p>'
            f'<p class="fee">Fee: ${amount}</p>'
        )
        response = HttpResponse(body, content_type='text/html')
    response['Content-Type'] = 'text/html'
    return response


@require_POST
def payment_api(request, loan_id):
    try:
        gateway_response = payment_application.charge(loan_id)
    except GatewayFailure as error:
        logger.warning('Payment gateway request failed', exc_info=error)
        return HttpResponse(
            'payment gateway unavailable\n',
            status=502,
            content_type='text/plain',
        )
    if gateway_response is None:
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')
    status = 200 if gateway_response.status_code == 200 else 502
    return HttpResponse(gateway_response.body, status=status, content_type='text/plain')


@require_GET
def fee_page(request, loan_id):
    quote = fee_application.quote(loan_id)
    if quote is None:
        return HttpResponse('<p>No such loan.</p>', status=404, content_type='text/html')
    return render(
        request,
        'fees/detail.html',
        {
            'quote': quote,
            'loan': quote.loan,
            'fee_amount': f'{quote.amount_cents // 100}.{quote.amount_cents % 100:02d}',
        },
    )


@require_POST
def payment_page(request, loan_id):
    gateway_error = False
    try:
        gateway_response = payment_application.charge(loan_id)
    except GatewayFailure as error:
        logger.warning('Payment gateway request failed', exc_info=error)
        gateway_response = None
        gateway_error = True

    if gateway_response is None and not gateway_error:
        return HttpResponse('<p>No such loan.</p>', status=404, content_type='text/html')

    if gateway_error or gateway_response.status_code != 200:
        status = 502
        message = (
            'Payment gateway unavailable.'
            if gateway_error or not gateway_response.body.strip()
            else gateway_response.body.strip()
        )
        template = 'fees/payment-status.html'
        context = {'message': message, 'success': False}
    else:
        status = 200
        template = 'fees/payment-status.html'
        context = {'message': 'Payment received.', 'success': True}

    if request.headers.get('HX-Request') == 'true':
        return render(request, template, context, status=status)
    if status == 200:
        return redirect(f'/ui/fees/{loan_id}/')
    quote = fee_application.quote(loan_id)
    return render(
        request,
        'fees/detail.html',
        {
            'quote': quote,
            'loan': quote.loan,
            'fee_amount': f'{quote.amount_cents // 100}.{quote.amount_cents % 100:02d}',
            'payment_error': context['message'],
        },
        status=status,
    )
