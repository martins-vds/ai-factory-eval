import logging

from django.http import HttpResponse
from django.utils.html import format_html
from django.views.decorators.http import require_GET, require_POST

from .composition import fee_application, payment_application
from .services import (
    PaymentGatewayInterrupted,
    PaymentGatewayUnavailable,
)

logger = logging.getLogger(__name__)


@require_GET
def late_fee(request, loan_id):
    quote = fee_application.quote_for(loan_id)
    if quote is None:
        return HttpResponse('<p>No such loan.</p>', status=404, content_type='text/html')

    body = format_html(
        '<h1>Late fee for {}</h1><p>Due {}, {} day(s) late.</p>'
        '<p class="fee">Fee: {}</p>',
        quote.loan.id,
        quote.loan.due_on.isoformat(),
        quote.days_late,
        quote.formatted_amount,
    )
    return HttpResponse(body, content_type='text/html')


@require_POST
def payment(request, loan_id):
    try:
        result = payment_application.pay(loan_id)
    except PaymentGatewayInterrupted as error:
        logger.warning('Payment gateway call interrupted', exc_info=error)
        return HttpResponse(
            'payment gateway unavailable\n',
            status=502,
            content_type='text/plain',
        )
    except PaymentGatewayUnavailable:
        return HttpResponse(
            'payment gateway unavailable\n',
            status=502,
            content_type='text/plain',
        )

    if result is None:
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')
    status = 200 if result.status_code == 200 else 502
    return HttpResponse(result.body, status=status, content_type='text/plain')
