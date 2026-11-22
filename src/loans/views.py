from django.http import HttpResponse
from django.shortcuts import render

from src.loans.repositories import DjangoLoanRepository
from src.loans.services import export_loans, format_loan, get_loan, list_loans


def loan_list(request):
    return HttpResponse(export_loans(DjangoLoanRepository()), content_type='text/plain')


def loan_detail(request, loan_id):
    loan = get_loan(DjangoLoanRepository(), loan_id)
    if loan is None:
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')
    return HttpResponse(format_loan(loan), content_type='text/plain')


def loan_catalog(request):
    loans = list_loans(DjangoLoanRepository())
    return render(request, 'loans/list.html', {'loans': loans})


def loan_page(request, loan_id):
    loan = get_loan(DjangoLoanRepository(), loan_id)
    if loan is None:
        return render(request, 'loans/not_found.html', status=404)
    return render(request, 'loans/detail.html', {'loan': loan})
