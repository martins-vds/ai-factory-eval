from django.http import HttpResponse

from src.loans.repository import DjangoLoanRepository

from .services import calculate_late_fee


def fee_detail(request, loan_id):
    loan = DjangoLoanRepository().find(loan_id)
    if loan is None:
        return HttpResponse('<p>No such loan.</p>', status=404, content_type='text/html')

    fee = calculate_late_fee(loan)
    body = (
        f'<h1>Late fee for {loan.id}</h1>'
        f'<p>Due {loan.due_on.isoformat()}, {fee.days_late} day(s) late.</p>'
        f'<p class="fee">Fee: ${fee.amount:.2f}</p>'
    )
    return HttpResponse(body, content_type='text/html')
