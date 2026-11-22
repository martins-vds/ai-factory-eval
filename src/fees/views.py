from django.http import HttpResponse
from django.shortcuts import render
from django.utils.html import format_html
from django.views.decorators.http import require_GET, require_POST

from .composition import fee_application, payment_application


@require_GET
def fee_api(request, loan_id):
    fee = fee_application.calculate(loan_id)
    if fee is None:
        return HttpResponse('<p>No such loan.</p>', status=404, content_type='text/html')

    body = format_html(
        '<h1>Late fee for {}</h1><p>Due {}, {} day(s) late.</p><p class="fee">Fee: {}</p>',
        fee.loan.id,
        fee.loan.due_on.isoformat(),
        fee.late_days,
        fee.amount,
    )
    return HttpResponse(body, content_type='text/html')


@require_GET
def fee_page(request, loan_id):
    fee = fee_application.calculate(loan_id)
    if fee is None:
        return render(request, 'fees/not-found.html', status=404)
    return render(request, 'fees/detail.html', {'fee': fee})


@require_POST
def payment_api(request, loan_id):
    result = payment_application.pay(loan_id)
    return HttpResponse(result.body, status=result.status, content_type='text/plain')


@require_POST
def payment_page(request, loan_id):
    result = payment_application.pay(loan_id)
    return render(
        request,
        'fees/payment-status.html',
        {'result': result, 'body': result.body.decode('utf-8', errors='replace').strip()},
        status=result.status,
    )
