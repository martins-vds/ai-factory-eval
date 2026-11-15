from django.http import HttpResponse

from src.loans.export import loan_line
from src.loans.repository import all_loans


def loan_list(request):
    return HttpResponse(
        ''.join(loan_line(loan) for loan in all_loans()),
        content_type='text/plain',
    )
