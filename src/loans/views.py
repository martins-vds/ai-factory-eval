from django.http import Http404, HttpResponse
from django.shortcuts import render

from src.loans.repositories import LoanRepository
from src.loans.services import export_loans


def loan_list(request):
    return HttpResponse(export_loans(LoanRepository().list()), content_type='text/plain')


def loan_detail(request, loan_id):
    loan = LoanRepository().get(loan_id)
    if loan is None:
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')
    return HttpResponse(export_loans([loan]), content_type='text/plain')


def catalog(request):
    return render(request, 'loans/catalog.html', {'loans': LoanRepository().list()})


def catalog_detail(request, loan_id):
    loan = LoanRepository().get(loan_id)
    if loan is None:
        raise Http404('No such loan.')
    return render(request, 'loans/detail.html', {'loan': loan})
