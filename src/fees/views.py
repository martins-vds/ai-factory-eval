import logging

from django.http import HttpResponse
from django.shortcuts import render
from django.utils.html import format_html
from django.views.decorators.http import require_GET, require_POST

from .composition import late_fee_application, payment_application
from .services import LoanNotFound, PaymentGatewayError

logger = logging.getLogger(__name__)


@require_GET
def fee_api(request, loan_id):
    try:
        quote = late_fee_application.calculate(loan_id)
    except LoanNotFound:
        return HttpResponse('<p>No such loan.</p>', status=404)

    return HttpResponse(
        format_html(
            '<h1>Late fee for {}</h1><p>Due {}, {} day(s) late.</p><p class="fee">Fee: ${}</p>',
            quote.loan_id,
            quote.due_on.isoformat(),
            quote.days_late,
            format(quote.amount, '.2f'),
        )
    )


@require_GET
def fee_page(request, loan_id):
    try:
        quote = late_fee_application.calculate(loan_id)
    except LoanNotFound:
        return render(request, 'fees/not-found.html', status=404)

    return render(
        request,
        'fees/fee-page.html',
        {
            'loan_id': quote.loan_id,
            'due_on': quote.due_on.isoformat(),
            'days_late': quote.days_late,
            'amount': format(quote.amount, '.2f'),
        },
    )


@require_POST
def payment_api(request, loan_id):
    try:
        gateway_response = payment_application.pay(loan_id)
    except LoanNotFound:
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')
    except PaymentGatewayError as error:
        logger.exception('Payment gateway failed for loan %s', loan_id, exc_info=error)
        return HttpResponse(
            'payment gateway unavailable\n',
            status=502,
            content_type='text/plain',
        )

    status = 200 if gateway_response.status == 200 else 502
    return HttpResponse(gateway_response.body, status=status, content_type='text/plain')


@require_POST
def payment_page(request, loan_id):
    try:
        gateway_response = payment_application.pay(loan_id)
        status = 200 if gateway_response.status == 200 else 502
        role = 'status' if status == 200 else 'alert'
        message = gateway_response.body
    except LoanNotFound:
        status = 404
        role = 'alert'
        message = 'No such loan.'
    except PaymentGatewayError as error:
        logger.exception('Payment gateway failed for loan %s', loan_id, exc_info=error)
        status = 502
        role = 'alert'
        message = 'payment gateway unavailable'

    template = (
        'fees/payment-result.html'
        if request.headers.get('HX-Request') == 'true'
        else 'fees/payment-result-page.html'
    )
    return render(
        request,
        template,
        {'role': role, 'message': message, 'loan_id': loan_id},
        status=status,
    )
