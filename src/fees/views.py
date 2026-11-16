from django.http import HttpResponse
from django.utils.html import format_html
from django.views.decorators.http import require_GET

from .composition import fee_application


def fee_body(quote):
    amount = f'${quote.amount_cents // 100}.{quote.amount_cents % 100:02d}'
    return format_html(
        '<h1>Late fee for {}</h1><p>Due {}, {} day(s) late.</p><p class="fee">Fee: {}</p>',
        quote.loan.id,
        quote.loan.due_on.isoformat(),
        quote.late_days,
        amount,
    )


@require_GET
def fee_detail(request, loan_id):
    quote = fee_application.quote(loan_id)
    if quote is None:
        return HttpResponse('<p>No such loan.</p>', status=404, content_type='text/html')
    return HttpResponse(fee_body(quote), content_type='text/html')
