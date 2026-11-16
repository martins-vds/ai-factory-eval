from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import render

from src.loans.export import export_loans
from src.loans.repository import LoanRepository


def loan_list(request):
    loans = LoanRepository().all()
    return HttpResponse(export_loans(loans), content_type='text/plain')


def loan_detail(request, loan_id):
    loan = LoanRepository().get(loan_id)
    if loan is None:
        return HttpResponseNotFound('no such loan\n', content_type='text/plain')
    return HttpResponse(export_loans([loan]), content_type='text/plain')


def loan_catalog(request):
    return render(request, 'loans/catalog.html', {'loans': LoanRepository().all()})


def loan_page(request, loan_id):
    loan = LoanRepository().get(loan_id)
    if loan is None:
        return render(request, 'loans/not_found.html', status=404)
    return render(request, 'loans/detail.html', {'loan': loan})
