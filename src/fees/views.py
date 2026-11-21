from django.http import HttpResponse
from django.views.decorators.http import require_GET, require_POST

from .composition import fee_application


@require_GET
def fee_api(request, loan_id):
    quote = fee_application.fee_for(loan_id)
    if quote is None:
        return HttpResponse('<p>No such loan.</p>', status=404, content_type='text/html')

    body = (
        f'<h1>Late fee for {quote.loan.id}</h1>'
        f'<p>Due {quote.loan.due_on.isoformat()}, {quote.late_days} day(s) late.</p>'
        f'<p class="fee">Fee: ${quote.amount:.2f}</p>'
    )
    return HttpResponse(body, content_type='text/html')


@require_POST
def payment_api(request, loan_id):
    result = fee_application.pay(loan_id)
    if result is None:
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')
    return HttpResponse(result.body, status=result.status_code, content_type='text/plain')
