from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render

from .dependencies import loan_catalog
from .services import LoanNotFound, format_loan


def api_list(request):
    return HttpResponse(loan_catalog.text_export(), content_type='text/plain')


def api_detail(request, loan_id):
    try:
        loan = loan_catalog.get_loan(loan_id)
    except LoanNotFound:
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')
    return HttpResponse(format_loan(loan), content_type='text/plain')


def catalog(request):
    return render(request, 'loans/catalog.html', {'loans': loan_catalog.list_loans()})


def catalog_detail(request, loan_id):
    try:
        loan = loan_catalog.get_loan(loan_id)
    except LoanNotFound:
        return render(request, 'loans/not_found.html', status=404)
    return render(request, 'loans/detail.html', {'loan': loan})
