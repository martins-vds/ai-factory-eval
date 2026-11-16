from django.http import HttpResponse
from django.utils import timezone
from django.utils.html import format_html

from src.loans.models import Loan

from .services import calculate_late_fee


def fee_endpoint(request, loan_id):
    loan = Loan.objects.filter(pk=loan_id).first()
    if loan is None:
        return HttpResponse('<p>No such loan.</p>', status=404, content_type='text/html')

    through = loan.returned_on or timezone.localdate()
    days_late, amount = calculate_late_fee(loan.due_on, through)
    body = format_html(
        '<h1>Late fee for {}</h1><p>Due {}, {} day(s) late.</p><p class="fee">Fee: ${}</p>',
        loan.id,
        loan.due_on.isoformat(),
        days_late,
        f'{amount:.2f}',
    )
    return HttpResponse(body, content_type='text/html')
