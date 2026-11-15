from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET, require_POST

from .composition import fees_application, payment_gateway
from .gateway import GatewayResponse, PaymentGatewayError


@require_GET
def fee_api(request, loan_id):
    fee = fees_application.fee_for(loan_id)
    if fee is None:
        return HttpResponse('<p>No such loan.</p>', status=404, content_type='text/html')

    body = (
        f'<h1>Late fee for {fee.loan.id}</h1>'
        f'<p>Due {fee.loan.due_on.isoformat()}, {fee.days_late} day(s) late.</p>'
        f'<p class="fee">Fee: ${fee.amount:.2f}</p>'
    )
    return HttpResponse(body, content_type='text/html')


@require_GET
def fee_page(request, loan_id):
    fee = fees_application.fee_for(loan_id)
    if fee is None:
        return HttpResponse('<p>No such loan.</p>', status=404, content_type='text/html')
    return render(request, 'fees/page.html', {'fee': fee})


@require_POST
def payment_api(request, loan_id):
    response = _payment_result(loan_id)
    if response is None:
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')

    return HttpResponse(
        response.body,
        status=response.status,
        content_type='text/plain',
    )


@require_POST
def payment_page(request, loan_id):
    response = _payment_result(loan_id)
    if response is None:
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')

    context = {'result': response}
    if request.headers.get('HX-Request') == 'true':
        return render(request, 'fees/payment-result.html', context)

    fee = fees_application.fee_for(loan_id)
    return render(request, 'fees/page.html', {'fee': fee, 'payment_result': response})


def _payment_result(loan_id):
    if fees_application.fee_for(loan_id) is None:
        return None

    try:
        response = payment_gateway.charge(loan_id)
    except PaymentGatewayError:
        return GatewayResponse(502, 'payment gateway unavailable\n')

    return GatewayResponse(200 if response.status == 200 else 502, response.body)
