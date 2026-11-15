from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render

from src.loans.export import loan_line
from src.loans.models import Loan
from src.loans.repository import all_loans, find_loan


def loan_list(request):
    return HttpResponse(
        ''.join(loan_line(loan) for loan in all_loans()),
        content_type='text/plain',
    )


def loan_detail(request, loan_id):
    loan = find_loan(loan_id)
    if loan is None:
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')
    return HttpResponse(loan_line(loan), content_type='text/plain')


def loan_catalog(request):
    return render(request, 'loans/list.html', {'loans': all_loans()})


def loan_page(request, loan_id):
    loan = get_object_or_404(Loan, pk=loan_id)
    return render(request, 'loans/detail.html', {'loan': loan})
