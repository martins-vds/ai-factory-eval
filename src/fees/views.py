from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET, require_POST

from .composition import fee_application, payment_application
from .services import PaymentInterrupted, PaymentResult


@require_GET
def fee_api(request, loan_id):
    fee = fee_application.for_loan(loan_id)
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
    fee = fee_application.for_loan(loan_id)
    return render(
        request,
        'fees/detail.html',
        {'fee': fee},
        status=404 if fee is None else 200,
    )


@require_POST
def payment_api(request, loan_id):
    try:
        result = payment_application.pay(loan_id)
    except PaymentInterrupted:
        return HttpResponse(
            'payment gateway unavailable\n',
            status=502,
            content_type='text/plain',
        )
    if result is None:
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')
    return HttpResponse(result.body, status=result.status, content_type='text/plain')


@require_POST
def payment_page(request, loan_id):
    try:
        result = payment_application.pay(loan_id)
    except PaymentInterrupted:
        result = PaymentResult(502, b'payment gateway unavailable\n')

    if result is None:
        result = PaymentResult(404, b'No such loan.')

    context = {
        'loan_id': loan_id,
        'success': result.status == 200,
        'message': result.body.decode('utf-8', errors='replace'),
    }
    if request.headers.get('HX-Request') == 'true':
        return render(
            request,
            'fees/payment-status.html',
            context,
            status=result.status,
        )
    return render(
        request,
        'fees/payment-result.html',
        context,
        status=result.status,
    )
