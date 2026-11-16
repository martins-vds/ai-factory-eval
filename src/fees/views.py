from django.http import HttpResponse
from django.shortcuts import render

from src.loans.models import Loan

from .services import calculate_late_fee


def _find_loan(loan_id):
    return Loan.objects.filter(pk=loan_id).first()


def fee_detail(request, loan_id):
    loan = _find_loan(loan_id)
    if loan is None:
        return HttpResponse('<p>No such loan.</p>', status=404, content_type='text/html')

    fee = calculate_late_fee(loan)
    return HttpResponse(
        f'<h1>Late fee for {loan.id}</h1>'
        f'<p>Due {loan.due_on.isoformat()}, {fee.days_late} day(s) late.</p>'
        f'<p class="fee">Fee: ${fee.amount:.2f}</p>',
        content_type='text/html',
    )


def fee_page(request, loan_id):
    loan = _find_loan(loan_id)
    if loan is None:
        return HttpResponse('<p>No such loan.</p>', status=404, content_type='text/html')

    return render(
        request,
        'fees/detail.html',
        {'loan': loan, 'fee': calculate_late_fee(loan)},
    )
