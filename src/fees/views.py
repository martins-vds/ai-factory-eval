from django.http import HttpResponse
from django.utils import timezone

from src.loans.models import Loan

from .services import calculate_late_fee


def fee_api(request, loan_id):
    loan = Loan.objects.filter(pk=loan_id).first()
    if loan is None:
        return HttpResponse('<p>No such loan.</p>', status=404, content_type='text/html')

    fee = calculate_late_fee(loan.due_on, loan.returned_on, timezone.localdate())
    body = (
        f'<h1>Late fee for {loan.id}</h1>'
        f'<p>Due {loan.due_on.isoformat()}, {fee.days_late} day(s) late.</p>'
        f'<p class="fee">Fee: {fee.formatted_amount}</p>'
    )
    return HttpResponse(body, content_type='text/html')
