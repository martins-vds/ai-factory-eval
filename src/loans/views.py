from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from .domain import LoanNotFound
from .repository import DjangoLoanRepository
from .services import LoanCatalog


def catalog_list(request: HttpRequest) -> HttpResponse:
    catalog = LoanCatalog(DjangoLoanRepository())
    return HttpResponse(catalog.export_loans(), content_type='text/plain')


def catalog_item(request: HttpRequest, loan_id: str) -> HttpResponse:
    catalog = LoanCatalog(DjangoLoanRepository())
    try:
        line = catalog.export_loan(loan_id)
    except LoanNotFound:
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')
    return HttpResponse(line, content_type='text/plain')


def catalog_page(request: HttpRequest) -> HttpResponse:
    loans = LoanCatalog(DjangoLoanRepository()).list_loans()
    return render(request, 'loans/catalog.html', {'loans': loans})


def loan_page(request: HttpRequest, loan_id: str) -> HttpResponse:
    catalog = LoanCatalog(DjangoLoanRepository())
    try:
        loan = catalog.get_loan(loan_id)
    except LoanNotFound:
        return render(request, 'loans/not_found.html', status=404, context={'loan_id': loan_id})
    return render(request, 'loans/detail.html', {'loan': loan})
