from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse

from .composition import fee_application
from .services import GatewayUnavailable, PaymentOutcome


def fee_api(request, loan_id):
    fee = fee_application.late_fee_for(loan_id)
    if fee is None:
        return HttpResponse('<p>No such loan.</p>', status=404, content_type='text/html')

    body = (
        f'<h1>Late fee for {fee.loan.id}</h1>'
        f'<p>Due {fee.loan.due_on.isoformat()}, {fee.days_late} day(s) late.</p>'
        f'<p class="fee">Fee: ${fee.amount}</p>'
    )
    return HttpResponse(body, content_type='text/html')


def fee_page(request, loan_id):
    fee = fee_application.late_fee_for(loan_id)
    if fee is None:
        return render(request, 'fees/not-found.html', status=404)
    return render(request, 'fees/fee.html', {'fee': fee})


def payment_api(request, loan_id):
    try:
        outcome = fee_application.pay(loan_id)
    except GatewayUnavailable as error:
        outcome = PaymentOutcome(502, str(error))

    if outcome is None:
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')
    return HttpResponse(outcome.body, status=outcome.status_code, content_type='text/plain')


def payment_page(request, loan_id):
    try:
        outcome = fee_application.pay(loan_id)
    except GatewayUnavailable as error:
        outcome = PaymentOutcome(502, str(error))

    if outcome is None:
        return render(request, 'fees/payment-status.html', {'payment_error': 'No such loan.'}, status=404)

    if outcome.status_code == 200:
        if request.headers.get('HX-Request') == 'true':
            return render(request, 'fees/payment-status.html', {'payment_body': outcome.body})
        return redirect(reverse('fee-page', kwargs={'loan_id': loan_id}))

    if request.headers.get('HX-Request') == 'true':
        return render(
            request,
            'fees/payment-status.html',
            {'payment_error': outcome.body},
            status=outcome.status_code,
        )
    fee = fee_application.late_fee_for(loan_id)
    return render(
        request,
        'fees/fee.html',
        {'fee': fee, 'payment_error': outcome.body},
        status=outcome.status_code,
    )
