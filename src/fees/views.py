from django.http import HttpResponse
from django.utils.html import format_html
from django.views.decorators.http import require_GET

from src.loans.models import Loan

from .services import calculate_late_fee


@require_GET
def late_fee(request, loan_id):
    loan = Loan.objects.filter(pk=loan_id).first()
    if loan is None:
        return HttpResponse('<p>No such loan.</p>', status=404, content_type='text/html')

    fee = calculate_late_fee(loan)
    body = format_html(
        '<h1>Late fee for {}</h1><p>Due {}, {} day(s) late.</p><p class="fee">Fee: ${}</p>',
        loan.id,
        fee.due_on.isoformat(),
        fee.days_late,
        format(fee.amount, '.2f'),
    )
    return HttpResponse(body, content_type='text/html')
