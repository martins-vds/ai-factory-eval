from django.http import HttpResponse

from src.loans.repositories import LoanRepository
from src.loans.services import export_loans


def loan_list(request):
    return HttpResponse(export_loans(LoanRepository().list()), content_type='text/plain')


def loan_detail(request, loan_id):
    loan = LoanRepository().get(loan_id)
    if loan is None:
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')
    return HttpResponse(export_loans([loan]), content_type='text/plain')
