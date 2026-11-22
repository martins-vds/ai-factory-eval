from django.http import HttpResponse

from src.loans.repositories import DjangoLoanRepository
from src.loans.services import export_loans


def loan_list(request):
    return HttpResponse(export_loans(DjangoLoanRepository()), content_type='text/plain')
