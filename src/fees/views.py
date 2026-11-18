from django.http import HttpResponse
from django.utils.html import format_html
from django.views.decorators.http import require_GET

from .composition import fee_application


@require_GET
def fee_detail(request, loan_id):
    fee = fee_application.calculate(loan_id)
    if fee is None:
        return HttpResponse('<p>No such loan.</p>', status=404, content_type='text/html')

    return HttpResponse(
        format_html(
            '<h1>Late fee for {}</h1><p>Due {}, {} day(s) late.</p>'
            '<p class="fee">Fee: ${}</p>',
            fee.loan_id,
            fee.due_on.isoformat(),
            fee.late_days,
            fee.formatted_amount,
        ),
        content_type='text/html',
    )
