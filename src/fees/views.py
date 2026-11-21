import logging

from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET, require_POST

from .composition import fee_application

logger = logging.getLogger(__name__)


@require_GET
def fee_api(request, loan_id):
    quote = fee_application.fee_for(loan_id)
    if quote is None:
        return HttpResponse('<p>No such loan.</p>', status=404, content_type='text/html')

    body = (
        f'<h1>Late fee for {quote.loan.id}</h1>'
        f'<p>Due {quote.loan.due_on.isoformat()}, {quote.late_days} day(s) late.</p>'
        f'<p class="fee">Fee: ${quote.amount:.2f}</p>'
    )
    return HttpResponse(body, content_type='text/html')


@require_GET
def fee_page(request, loan_id):
    quote = fee_application.fee_for(loan_id)
    return render(
        request,
        'fees/page.html',
        {'quote': quote},
        status=404 if quote is None else 200,
    )


@require_POST
def payment_api(request, loan_id):
    result = fee_application.pay(loan_id)
    if result is None:
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')
    if result.failure is not None:
        logger.warning('Payment gateway request failed', exc_info=result.failure)
    return HttpResponse(result.body, status=result.status_code, content_type='text/plain')


@require_POST
def payment_page(request, loan_id):
    result = fee_application.pay(loan_id)
    if result is None:
        if request.headers.get('HX-Request') == 'true':
            return render(
                request,
                'fees/payment-panel.html',
                {'loan_id': loan_id, 'not_found': True},
                status=404,
            )
        return render(request, 'fees/page.html', {'quote': None}, status=404)

    if result.failure is not None:
        logger.warning('Payment gateway request failed', exc_info=result.failure)
    if request.headers.get('HX-Request') == 'true':
        return render(
            request,
            'fees/payment-panel.html',
            {'loan_id': loan_id, 'payment': result},
            status=result.status_code,
        )

    quote = fee_application.fee_for(loan_id)
    return render(
        request,
        'fees/page.html',
        {'quote': quote, 'payment': result},
        status=result.status_code,
    )
