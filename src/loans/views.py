from django.http import HttpResponse

from src.loans.formatting import loan_line
from src.loans.repository import get_loan, list_loans


def loan_list(request):
    return HttpResponse(
        ''.join(loan_line(loan) for loan in list_loans()),
        content_type='text/plain',
    )


def loan_detail(request, loan_id):
    loan = get_loan(loan_id)
    if loan is None:
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')
    return HttpResponse(loan_line(loan), content_type='text/plain')
