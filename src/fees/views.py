from django.http import HttpResponse
from django.shortcuts import render
from django.utils.html import format_html
from django.views.decorators.http import require_GET, require_POST

from .composition import fee_application, payment_application


@require_GET
def fee_api(request, loan_id):
    fee = fee_application.fee_for(loan_id)
    if fee is None:
        return HttpResponse('<p>No such loan.</p>', status=404, content_type='text/html')

    content = format_html(
        '<h1>Late fee for {}</h1><p>Due {}, {} day(s) late.</p><p class="fee">Fee: ${}</p>',
        fee.loan.id,
        fee.loan.due_on.isoformat(),
        fee.late_days,
        f'{fee.amount:.2f}',
    )
    return HttpResponse(content, content_type='text/html')


@require_GET
def fee_page(request, loan_id):
    fee = fee_application.fee_for(loan_id)
    if fee is None:
        return render(request, 'fees/not-found.html', status=404)

    return render(request, 'fees/page.html', {'fee': fee})


@require_POST
def payment_api(request, loan_id):
    payment = payment_application.pay(loan_id)
    if payment is None:
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')

    return HttpResponse(payment.body, status=payment.status_code, content_type='text/plain')


@require_POST
def payment_page(request, loan_id):
    payment = payment_application.pay(loan_id)
    if payment is None:
        context = {'payment_status': 404, 'payment_message': 'No such loan.'}
        status = 404
    else:
        context = {'payment_status': payment.status_code, 'payment_message': payment.body}
        status = payment.status_code

    template = (
        'fees/payment-status.html'
        if request.headers.get('HX-Request') == 'true'
        else 'fees/payment-result.html'
    )
    return render(request, template, context, status=status)
