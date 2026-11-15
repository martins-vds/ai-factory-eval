from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET

from .composition import fee_application


@require_GET
def late_fee(request, loan_id):
    quote = fee_application.quote(loan_id)
    if quote is None:
        return HttpResponse('<p>No such loan.</p>', status=404, content_type='text/html')

    body = (
        f'<h1>Late fee for {quote.loan.id}</h1>'
        f'<p>Due {quote.loan.due_on.isoformat()}, {quote.days_late} day(s) late.</p>'
        f'<p class="fee">Fee: {quote.formatted_amount}</p>'
    )
    return HttpResponse(body, content_type='text/html')


@require_GET
def late_fee_page(request, loan_id):
    quote = fee_application.quote(loan_id)
    if quote is None:
        return HttpResponse('<p>No such loan.</p>', status=404, content_type='text/html')
    return render(
        request,
        'fees/late-fee.html',
        {'loan': quote.loan, 'days_late': quote.days_late, 'fee': quote.formatted_amount},
    )
