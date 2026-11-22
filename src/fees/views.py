import logging

from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET, require_POST

from .composition import fee_application

logger = logging.getLogger(__name__)


@require_GET
def fee_detail(request, loan_id):
    quote = fee_application.quote(loan_id)
    if quote is None:
        response = HttpResponse('<p>No such loan.</p>', status=404)
        response['Content-Type'] = 'text/html'
        return response

    return HttpResponse(
        f'<h1>Late fee for {quote.loan.id}</h1>'
        f'<p>Due {quote.loan.due_on.isoformat()}, {quote.late_days} day(s) late.</p>'
        f'<p class="fee">Fee: {quote.amount}</p>',
        content_type='text/html',
    )


@require_GET
def fee_page(request, loan_id):
    quote = fee_application.quote(loan_id)
    if quote is None:
        return render(request, 'fees/not-found.html', status=404)
    return render(request, 'fees/page.html', {'quote': quote})


def _payment_outcome(loan_id):
    outcome = fee_application.pay(loan_id)
    if (
        outcome is not None
        and outcome.failure is not None
        and isinstance(
            outcome.failure.__cause__,
            InterruptedError,
        )
    ):
        logger.warning(
            'Payment gateway request was interrupted',
            exc_info=(
                type(outcome.failure),
                outcome.failure,
                outcome.failure.__traceback__,
            ),
        )
    return outcome


@require_POST
def payment_detail(request, loan_id):
    outcome = _payment_outcome(loan_id)
    if outcome is None:
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')
    return HttpResponse(outcome.body, status=outcome.status_code, content_type='text/plain')


@require_POST
def payment_page(request, loan_id):
    outcome = _payment_outcome(loan_id)
    if outcome is None:
        return render(
            request,
            'fees/payment-status.html',
            {'success': False, 'body': 'no such loan\n'},
            status=404,
        )
    return render(
        request,
        'fees/payment-status.html',
        {'success': outcome.status_code == 200, 'body': outcome.body},
        status=outcome.status_code,
    )
