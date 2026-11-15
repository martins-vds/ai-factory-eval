from django.http import HttpResponse

from src.loans.formatting import format_loans
from src.loans.repositories import list_loans


def loan_list(request):
    return HttpResponse(format_loans(list_loans()), content_type='text/plain')
