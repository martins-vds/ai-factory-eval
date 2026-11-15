import logging

from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.utils.html import format_html
from django.views.decorators.http import require_GET, require_POST

from .composition import fee_application, payment_application
from .services import (
    GatewayResponse,
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
        '<h1>Late fee for {}</h1><p>Due {}, {} day(s) late.</p><p class="fee">Fee: {}</p>',
        quote.loan.id,
        quote.loan.due_on.isoformat(),
        quote.days_late,
        quote.formatted_amount,
    )
    return HttpResponse(body, content_type='text/html')


@require_POST
def payment(request, loan_id):
    result = _payment_result(loan_id)
    if result is None:
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')
    status = 200 if result.status_code == 200 else 502
    return HttpResponse(result.body, status=status, content_type='text/plain')


@require_GET
def late_fee_page(request, loan_id):
    return _render_fee_page(request, loan_id)


@require_POST
def payment_page(request, loan_id):
    result = _payment_result(loan_id)
    is_htmx = request.headers.get('HX-Request') == 'true'
    if result is None:
        if is_htmx:
            return render(
                request,
                'fees/payment-status.html',
                {
                    'feedback': {
                        'success': False,
                        'message': 'No such loan.',
                        'gateway_body': '',
                    }
                },
            )
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')

    success = result.status_code == 200
    feedback = {
        'loan_id': loan_id,
        'success': success,
        'message': (
            f'Payment complete for {loan_id}.' if success else 'Payment could not be completed.'
        ),
        'gateway_body': result.body,
    }
    if is_htmx:
        return render(request, 'fees/payment-status.html', {'feedback': feedback})
    if success:
        return redirect('late-fee-page', loan_id=loan_id)
    return _render_fee_page(request, loan_id, feedback, status=502)


def _render_fee_page(request, loan_id, payment_feedback=None, status=200):
    quote = fee_application.quote_for(loan_id)
    if quote is None:
        return HttpResponse('<p>No such loan.</p>', status=404, content_type='text/html')
    return render(
        request,
        'fees/page.html',
        {'quote': quote, 'payment_feedback': payment_feedback},
        status=status,
    )


def _payment_result(loan_id):
    try:
        result = payment_application.pay(loan_id)
    except PaymentGatewayInterrupted as error:
        logger.warning('Payment gateway call interrupted', exc_info=error)
        return GatewayResponse(502, 'payment gateway unavailable\n')
    except PaymentGatewayUnavailable:
        return GatewayResponse(502, 'payment gateway unavailable\n')
    return result
