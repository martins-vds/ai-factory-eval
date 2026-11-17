from django.http import HttpResponse

from src.loans.repositories import LoanRepository
from src.loans.services import export_loans


def loan_list(request):
    return HttpResponse(export_loans(LoanRepository().list()), content_type='text/plain')
