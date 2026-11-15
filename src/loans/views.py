from django.http import Http404, HttpResponse
from django.shortcuts import render

from src.loans.export import format_loan, format_loans
from src.loans.repository import LoanRepository


def list_loans(request):
    return HttpResponse(format_loans(LoanRepository.list_all()), content_type='text/plain')


def get_loan(request, loan_id):
    loan = LoanRepository.get_by_id(loan_id)
    if loan is None:
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')
    return HttpResponse(format_loan(loan), content_type='text/plain')


def catalog(request):
    return render(request, 'loans/list.html', {'loans': LoanRepository.list_all()})


def catalog_detail(request, loan_id):
    loan = LoanRepository.get_by_id(loan_id)
    if loan is None:
        raise Http404
    return render(request, 'loans/detail.html', {'loan': loan})
