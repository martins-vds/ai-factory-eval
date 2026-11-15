from django.http import HttpResponse, HttpResponseNotFound

from src.loans.formatting import format_loan, format_loans
from src.loans.repositories import get_loan, list_loans


def loan_list(request):
    return HttpResponse(format_loans(list_loans()), content_type='text/plain')


def loan_detail(request, loan_id):
    loan = get_loan(loan_id)
    if loan is None:
        return HttpResponseNotFound('no such loan\n', content_type='text/plain')
    return HttpResponse(format_loan(loan), content_type='text/plain')
