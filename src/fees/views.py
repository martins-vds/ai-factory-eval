from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET, require_POST

from .composition import fee_application


@require_GET
def fee_api(request, loan_id):
    fee = fee_application.fee_for(loan_id)
    if fee is None:
        return HttpResponse('<p>No such loan.</p>', status=404, content_type='text/html')

    amount = f'{fee.amount:.2f}'
    body = (
        f'<h1>Late fee for {fee.loan.id}</h1>'
        f'<p>Due {fee.loan.due_on}, {fee.days_late} day(s) late.</p>'
        f'<p class="fee">Fee: ${amount}</p>'
    )
    return HttpResponse(body, content_type='text/html')


@require_GET
def fee_page(request, loan_id):
    fees = fee_application.fees()
    fee = next((item for item in fees if item.loan.id == loan_id), None)
    if fee is None:
        return render(request, 'fees/not-found.html', status=404)
    return render(request, 'fees/late-fee.html', {'fee': fee, 'fees': fees})


@require_POST
def payment_api(request, loan_id):
    result = fee_application.pay(loan_id)
    return HttpResponse(result.body, status=result.status, content_type='text/plain')


@require_POST
def payment_page(request, loan_id):
    result = fee_application.pay(loan_id)
    if request.headers.get('HX-Request') == 'true':
        return render(
            request,
            'fees/payment-result.html',
            {'result': result},
            status=result.status,
        )

    fee = fee_application.fee_for(loan_id)
    if fee is None:
        return render(request, 'fees/not-found.html', status=404)
    return render(
        request,
        'fees/late-fee.html',
        {'fee': fee, 'fees': fee_application.fees(), 'payment_result': result},
        status=result.status,
    )
