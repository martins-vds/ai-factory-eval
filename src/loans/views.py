from django.http import HttpResponse
from django.shortcuts import render

from src.loans.repositories import LoanRepository
from src.loans.services import CatalogService


catalog = CatalogService(LoanRepository())


def loans(request):
    loans = catalog.list_loans()
    text = ''.join(catalog.export_line(loan) for loan in loans)
    return HttpResponse(text, content_type='text/plain')


def loan_detail(request, loan_id):
    loan = catalog.get_loan(loan_id)
    if loan is None:
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')
    return HttpResponse(catalog.export_line(loan), content_type='text/plain')


def loan_detail_ui(request, loan_id):
    loan = catalog.get_loan(loan_id)
    if loan is None:
        return HttpResponse('No such loan.', status=404)
    return render(request, 'loans/detail.html', {'loan': loan})


def loan_list_ui(request):
    loans = catalog.list_loans()
    return render(request, 'loans/list.html', {'loans': loans})
