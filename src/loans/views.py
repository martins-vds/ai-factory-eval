from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET

from src.loans.composition import loan_catalog
from src.loans.services import LoanNotFound


@require_GET
def loan_list(request: HttpRequest) -> HttpResponse:
    return HttpResponse(loan_catalog().export_text(), content_type='text/plain')


@require_GET
def loan_detail(request: HttpRequest, loan_id: str) -> HttpResponse:
    catalog = loan_catalog()
    try:
        loan = catalog.get_loan(loan_id)
    except LoanNotFound:
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')
    return HttpResponse(catalog.loan_text(loan), content_type='text/plain')


@require_GET
def catalog_page(request: HttpRequest) -> HttpResponse:
    return render(request, 'loans/catalog.html', {'loans': loan_catalog().list_loans()})


@require_GET
def loan_page(request: HttpRequest, loan_id: str) -> HttpResponse:
    catalog = loan_catalog()
    try:
        loan = catalog.get_loan(loan_id)
    except LoanNotFound:
        return render(request, 'loans/not_found.html', status=404)
    return render(request, 'loans/detail.html', {'loan': loan})
