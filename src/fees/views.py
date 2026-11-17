from django.http import HttpResponse
from django.shortcuts import render
from django.utils.html import escape
from django.views.decorators.http import require_GET

from .composition import fee_application


@require_GET
def fee_detail(request, loan_id):
    result = fee_application.get(loan_id)
    if result is None:
        return HttpResponse(
            '<p>No such loan.</p>',
            status=404,
            content_type='text/html',
        )

    loan, fee = result
    body = (
        f'<h1>Late fee for {escape(loan.id)}</h1>'
        f'<p>Due {loan.due_on.isoformat()}, {fee.late_days} day(s) late.</p>'
        f'<p class="fee">Fee: {fee.amount}</p>'
    )
    return HttpResponse(body, content_type='text/html')
