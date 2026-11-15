from django.http import HttpResponse
from django.utils.html import format_html
from django.views.decorators.http import require_GET

from .composition import fee_application


@require_GET
def late_fee(request, loan_id):
    quote = fee_application.quote_for(loan_id)
    if quote is None:
        return HttpResponse('<p>No such loan.</p>', status=404, content_type='text/html')

    body = format_html(
        '<h1>Late fee for {}</h1><p>Due {}, {} day(s) late.</p>'
        '<p class="fee">Fee: {}</p>',
        quote.loan.id,
        quote.loan.due_on.isoformat(),
        quote.days_late,
        quote.formatted_amount,
    )
    return HttpResponse(body, content_type='text/html')
