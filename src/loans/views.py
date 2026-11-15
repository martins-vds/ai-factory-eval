from django.http import Http404, HttpResponse
from django.shortcuts import render

from src.loans.formatting import format_loan, format_loans
from src.loans.repository import all_loans, find_loan


def loan_list(request):
    return HttpResponse(format_loans(all_loans()), content_type='text/plain')


def loan_detail(request, loan_id):
    loan = find_loan(loan_id)
    if loan is None:
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')
    return HttpResponse(format_loan(loan), content_type='text/plain')


def loan_catalog(request):
    return render(request, 'loans/list.html', {'loans': all_loans()})


def loan_page(request, loan_id):
    loan = find_loan(loan_id)
    if loan is None:
        raise Http404
    return render(request, 'loans/detail.html', {'loan': loan})
