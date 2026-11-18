from django.http import HttpResponse

from .composition import fee_application


def fee_api(request, loan_id):
    quote = fee_application.quote(loan_id)
    if quote is None:
        response = HttpResponse('<p>No such loan.</p>', status=404, content_type='text/html')
    else:
        amount = f'{quote.amount_cents // 100}.{quote.amount_cents % 100:02d}'
        body = (
            f'<h1>Late fee for {quote.loan.id}</h1>'
            f'<p>Due {quote.loan.due_on.isoformat()}, {quote.days_late} day(s) late.</p>'
            f'<p class="fee">Fee: ${amount}</p>'
        )
        response = HttpResponse(body, content_type='text/html')
    response['Content-Type'] = 'text/html'
    return response
