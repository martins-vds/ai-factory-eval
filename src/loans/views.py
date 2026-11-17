from django.http import HttpResponse

from src.loans.export import loan_line
from src.loans.repository import LoanRepository


def _text_response(body, status=200):
    response = HttpResponse(body, status=status, content_type='text/plain')
    response['Content-Type'] = 'text/plain'
    return response


def loan_list(request):
    body = ''.join(f'{loan_line(loan)}\n' for loan in LoanRepository.all())
    return _text_response(body)


def loan_detail(request, loan_id):
    loan = LoanRepository.find(loan_id)
    if loan is None:
        return _text_response('no such loan\n', status=404)
    return _text_response(f'{loan_line(loan)}\n')
