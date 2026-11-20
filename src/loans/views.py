from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render

from src.loans.models import Loan
from src.loans.repository import LoanRepository
from src.loans.services import format_loan

repository = LoanRepository()


def list_loans(_request):
    lines = [format_loan(loan) for loan in repository.list()]
    return HttpResponse('\n'.join(lines) + ('\n' if lines else ''), content_type='text/plain')


def get_loan(request, loan_id):
    loan = repository.get(loan_id)
    if loan is None:
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')
    return HttpResponse(format_loan(loan) + '\n', content_type='text/plain')


def ui_list(request):
    loans = repository.list()
    return render(request, 'loans/list.html', {'loans': loans})


def ui_detail(request, loan_id):
    loan = get_object_or_404(Loan, id=loan_id)
    return render(request, 'loans/detail.html', {'loan': loan})
