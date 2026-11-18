from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET

from .composition import fee_application


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
