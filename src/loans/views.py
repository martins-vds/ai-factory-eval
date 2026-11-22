from django.http import HttpRequest, HttpResponse

from src.loans.repository import DjangoLoanRepository
from src.loans.services import format_loan, get_loan, list_loans


def loan_list_api(request: HttpRequest) -> HttpResponse:
    repository = DjangoLoanRepository()
    body = ''.join(format_loan(loan) for loan in list_loans(repository))
    return HttpResponse(body, content_type='text/plain')


def loan_detail_api(request: HttpRequest, loan_id: str) -> HttpResponse:
    loan = get_loan(DjangoLoanRepository(), loan_id)
    if loan is None:
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')
    return HttpResponse(format_loan(loan), content_type='text/plain')
