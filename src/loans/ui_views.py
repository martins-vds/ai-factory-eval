from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from src.loans.repository import DjangoLoanRepository
from src.loans.services import get_loan, list_loans, loan_due_date


def loan_catalog_page(request: HttpRequest) -> HttpResponse:
    loans = [
        {'loan': loan, 'due_on': loan_due_date(loan)}
        for loan in list_loans(DjangoLoanRepository())
    ]
    return render(request, 'loans/list.html', {'loans': loans})


def loan_detail_page(request: HttpRequest, loan_id: str) -> HttpResponse:
    loan = get_loan(DjangoLoanRepository(), loan_id)
    if loan is None:
        return render(request, 'loans/not_found.html', status=404)
    return render(
        request,
        'loans/detail.html',
        {'loan': loan, 'due_on': loan_due_date(loan)},
    )
