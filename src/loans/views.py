from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render

from src.loans.models import Loan
from src.loans.repository import find_loan, list_loans
from src.loans.services import format_loan


def loan_list(request):
    body = ''.join(format_loan(loan) for loan in list_loans())
    return HttpResponse(body, content_type='text/plain')


def loan_detail(request, loan_id):
    loan = find_loan(loan_id)
    if loan is None:
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')
    return HttpResponse(format_loan(loan), content_type='text/plain')


def loan_catalog(request):
    return render(request, 'loans/list.html', {'loans': list_loans()})


def loan_catalog_detail(request, loan_id):
    loan = get_object_or_404(Loan, pk=loan_id)
    return render(request, 'loans/detail.html', {'loan': loan})
