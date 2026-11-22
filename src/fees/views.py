from django.http import HttpResponse
from django.shortcuts import render
from django.utils.html import format_html
from django.views.decorators.http import require_GET, require_POST

from .composition import fee_application, payment_application


def fee_amount(cents):
    return f'{cents // 100}.{cents % 100:02d}'


@require_GET
def fee_api(request, loan_id):
    fee = fee_application.calculate(loan_id)
    if fee is None:
        return HttpResponse('<p>No such loan.</p>', status=404, content_type='text/html')

    content = format_html(
        '<h1>Late fee for {}</h1><p>Due {}, {} day(s) late.</p><p class="fee">Fee: ${}</p>',
        fee.loan_id,
        fee.due_on.isoformat(),
        fee.days_late,
        fee_amount(fee.amount_cents),
    )
    return HttpResponse(content, content_type='text/html')


@require_GET
def fee_page(request, loan_id):
    fee = fee_application.calculate(loan_id)
    return render(
        request,
        'fees/page.html',
        {'fee': fee, 'fee_amount': fee_amount(fee.amount_cents) if fee else None},
        status=200 if fee else 404,
    )


@require_POST
def payment_api(request, loan_id):
    result = payment_application.pay(loan_id)
    return HttpResponse(result.body, status=result.status, content_type='text/plain')


@require_POST
def payment_page(request, loan_id):
    result = payment_application.pay(loan_id)
    message = result.body.decode('utf-8', errors='replace')
    return render(
        request,
        'fees/payment-result.html',
        {'message': message, 'success': result.status == 200},
        status=result.status,
    )
