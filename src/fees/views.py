from django.http import HttpResponse
from django.utils import timezone

from src.loans.models import Loan

from .services import calculate_late_fee


def fee_detail(request, loan_id):
    loan = Loan.objects.filter(pk=loan_id).first()
    if loan is None:
        return HttpResponse('<p>No such loan.</p>', status=404, content_type='text/html')

    fee = calculate_late_fee(loan.due_on, loan.returned_on, timezone.localdate())
    return HttpResponse(
        f'<h1>Late fee for {loan.id}</h1><p>Due {loan.due_on.isoformat()}, '
        f'{fee.days_late} day(s) late.</p><p class="fee">Fee: ${fee.amount:.2f}</p>',
        content_type='text/html',
    )
