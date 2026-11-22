from django.http import HttpResponse
from django.shortcuts import render

from src.loans.repository import DjangoLoanRepository
from src.loans.services import LoanCatalog


def _catalog() -> LoanCatalog:
    return LoanCatalog(DjangoLoanRepository())


def _plain_text(body: str, status: int = 200) -> HttpResponse:
    response = HttpResponse(body, status=status, content_type='text/plain')
    response['Content-Type'] = 'text/plain'
    return response


def api_list(request):
    catalog = _catalog()
    lines = (catalog.format_loan(loan) for loan in catalog.list_loans())
    return _plain_text(''.join(lines))


def api_detail(request, loan_id: str):
    loan = _catalog().get_loan(loan_id)
    if loan is None:
        return _plain_text('no such loan\n', status=404)
    return _plain_text(LoanCatalog.format_loan(loan))


def ui_list(request):
    return render(request, 'loans/list.html', {'loans': _catalog().list_loans()})


def ui_detail(request, loan_id: str):
    loan = _catalog().get_loan(loan_id)
    if loan is None:
        return render(request, 'loans/not_found.html', status=404)
    return render(request, 'loans/detail.html', {'loan': loan})
