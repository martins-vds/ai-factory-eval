from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET
from django.views.decorators.http import require_POST

from .composition import fees_application, payment_gateway
from .gateway import PaymentGatewayError


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
    if fees_application.fee_for(loan_id) is None:
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')

    try:
        response = payment_gateway.charge(loan_id)
    except PaymentGatewayError:
        return HttpResponse('payment gateway unavailable\n', status=502, content_type='text/plain')

    return HttpResponse(
        response.body,
        status=200 if response.status == 200 else 502,
        content_type='text/plain',
    )
