from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from .repository import DjangoLoanRepository
from .services import LoanCatalog


def _catalog() -> LoanCatalog:
    return LoanCatalog(DjangoLoanRepository())


def loan_list(request: HttpRequest) -> HttpResponse:
    response = HttpResponse(_catalog().text_export())
    response['Content-Type'] = 'text/plain'
    return response


def loan_detail(request: HttpRequest, loan_id: str) -> HttpResponse:
    loan = _catalog().get(loan_id)
    if loan is None:
        response = HttpResponse('no such loan\n', status=404)
    else:
        response = HttpResponse(f'{LoanCatalog.text_line(loan)}\n')
    response['Content-Type'] = 'text/plain'
    return response


def catalog_page(request: HttpRequest) -> HttpResponse:
    loans = _catalog().all()
    return render(request, 'loans/list.html', {'loans': loans})


def loan_page(request: HttpRequest, loan_id: str) -> HttpResponse:
    loan = _catalog().get(loan_id)
    if loan is None:
        return render(request, 'loans/not_found.html', status=404)
    return render(request, 'loans/detail.html', {'loan': loan})
