from django.http import HttpResponse

from src.loans.formatting import loan_line
from src.loans.repository import list_loans


def loan_list(request):
    return HttpResponse(
        ''.join(loan_line(loan) for loan in list_loans()),
        content_type='text/plain',
    )
