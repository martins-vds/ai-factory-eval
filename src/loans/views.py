from django.http import HttpResponse
from django.shortcuts import render

from src.loans.repository import DjangoLoanRepository
from src.loans.services import ExportLoans, GetLoan, ListLoans, LoanNotFound


def api_loan_list(request):
    repository = DjangoLoanRepository()
    return HttpResponse(ExportLoans(repository).execute(), content_type='text/plain')


def api_loan_detail(request, loan_id):
    try:
        loan = GetLoan(DjangoLoanRepository()).execute(loan_id)
    except LoanNotFound:
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')
    return HttpResponse(
        ExportLoans(DjangoLoanRepository()).execute([loan]), content_type='text/plain'
    )


def loan_catalog(request):
    loans = ListLoans(DjangoLoanRepository()).execute()
    return render(request, 'loans/catalog.html', {'loans': loans})


def ui_loan_detail(request, loan_id):
    try:
        loan = GetLoan(DjangoLoanRepository()).execute(loan_id)
    except LoanNotFound:
        if request.headers.get('HX-Request') == 'true':
            return render(request, 'loans/detail_error.html', status=404)
        return render(request, 'loans/not_found.html', status=404)
    if request.headers.get('HX-Request') == 'true':
        return render(request, 'loans/detail_fragment.html', {'loan': loan})
    return render(request, 'loans/detail.html', {'loan': loan})
