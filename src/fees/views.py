from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.http import require_POST

from .composition import fee_application, payment_application


def fee_detail(request, loan_id):
    fee = fee_application.calculate(loan_id)
    if fee is None:
        return HttpResponse(
            '<p>No such loan.</p>',
            status=404,
            content_type='text/html',
        )
    body = (
        f'<h1>Late fee for {fee.loan_id}</h1>'
        f'<p>Due {fee.due_on.isoformat()}, {fee.late_days} day(s) late.</p>'
        f'<p class="fee">Fee: ${fee.amount:.2f}</p>'
    )
    return HttpResponse(body, content_type='text/html')


@require_POST
def payment(request, loan_id):
    _outcome, status, body = payment_application.pay(loan_id)
    return HttpResponse(body, status=status, content_type='text/plain')


def fee_page(request, loan_id):
    fee = fee_application.calculate(loan_id)
    if fee is None:
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')
    return render(request, 'fees/detail.html', {'fee': fee})


@require_POST
def fee_payment_page(request, loan_id):
    _outcome, status, body = payment_application.pay(loan_id)
    if request.headers.get('HX-Request') == 'true':
        if status == 200:
            return render(request, 'fees/payment-success.html', {'body': body})
        return render(
            request,
            'fees/payment-error.html',
            {'body': body},
            status=status,
        )
    if status != 200:
        return HttpResponse(body, status=status, content_type='text/plain')
    return HttpResponse(
        status=302, headers={'Location': reverse('fee-page', kwargs={'loan_id': loan_id})}
    )
