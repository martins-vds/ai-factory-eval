from django.http import HttpResponse
from django.shortcuts import render

from src.loans.formatting import loan_line
from src.loans.repositories import LoanRepository


def loan_list(request):
    return HttpResponse(
        ''.join(loan_line(loan) for loan in LoanRepository.all()),
        content_type='text/plain',
    )


def loan_detail(request, loan_id):
    loan = LoanRepository.find(loan_id)
    if loan is None:
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')
    return HttpResponse(loan_line(loan), content_type='text/plain')


def ui_loan_list(request):
    return render(request, 'loans/list.html', {'loans': LoanRepository.all()})


def ui_loan_detail(request, loan_id):
    loan = LoanRepository.find(loan_id)
    if loan is None:
        return render(request, 'loans/not_found.html', status=404, context={'loan_id': loan_id})
    return render(request, 'loans/detail.html', {'loan': loan})
