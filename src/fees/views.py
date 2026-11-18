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
    try:
        gateway_response = payment_application.charge(loan_id)
    except GatewayFailure as error:
        logger.warning('Payment gateway request failed', exc_info=error)
        return _payment_failure(request, loan_id, 'Payment gateway unavailable.')
    if gateway_response is None:
        return HttpResponse('<p>No such loan.</p>', status=404, content_type='text/html')
    if request.headers.get('HX-Request') == 'true':
        if gateway_response.status_code != 200:
            message = gateway_response.body.strip() or 'Payment gateway unavailable.'
            return _payment_failure(request, loan_id, message)
        return render(
            request,
            'fees/payment-status.html',
            {'message': 'Payment received.', 'success': True},
        )
    if gateway_response.status_code == 200:
        return redirect('fee_page', loan_id=loan_id)
    message = gateway_response.body.strip() or 'Payment gateway unavailable.'
    return _payment_failure(request, loan_id, message)


def _payment_failure(request, loan_id, message):
    if request.headers.get('HX-Request') == 'true':
        return render(
            request,
            'fees/payment-status.html',
            {'message': message, 'success': False},
            status=502,
        )
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
            'payment_error': message,
        },
        status=502,
    )
