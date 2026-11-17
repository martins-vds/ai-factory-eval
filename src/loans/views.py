from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render

from src.loans.export import loan_line
from src.loans.models import Loan
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


def loan_catalog(request):
    return render(request, 'loans/list.html', {'loans': LoanRepository.all()})


def loan_page(request, loan_id):
    loan = get_object_or_404(Loan, pk=loan_id)
    return render(request, 'loans/detail.html', {'loan': loan})
