from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.utils.html import format_html
from django.views.decorators.http import require_GET, require_POST

from .composition import fee_application, payment_application


@require_GET
def fee_api(request, loan_id):
    fee = fee_application.calculate(loan_id)
    if fee is None:
        return HttpResponse('<p>No such loan.</p>', status=404, content_type='text/html')

    body = format_html(
        '<h1>Late fee for {}</h1><p>Due {}, {} day(s) late.</p><p class="fee">Fee: ${}</p>',
        fee.loan_id,
        fee.due_on.isoformat(),
        fee.late_days,
        f'{fee.amount:.2f}',
    )
    return HttpResponse(body, content_type='text/html')


@require_GET
def fee_page(request, loan_id):
    fee = fee_application.calculate(loan_id)
    if fee is None:
        return render(request, 'fees/not-found.html', status=404)
    return render(request, 'fees/detail.html', {'fee': fee})


def _payment_outcome(loan_id):
    result = payment_application.pay(loan_id)
    if result is None:
        return False, 'no such loan\n', 404
    return result.status_code == 200, result.body, result.status_code


@csrf_exempt
@require_POST
def payment_api(request, loan_id):
    _, body, status = _payment_outcome(loan_id)
    return HttpResponse(body, status=status, content_type='text/plain')


@require_POST
def payment_page(request, loan_id):
    succeeded, body, status = _payment_outcome(loan_id)
    context = {'loan_id': loan_id, 'succeeded': succeeded, 'payment_body': body}

    if request.headers.get('HX-Request') == 'true':
        return render(request, 'fees/payment-status.html', context)
    return render(request, 'fees/payment-result.html', context, status=status)
