from django.http import Http404, HttpResponse
from django.shortcuts import render

from .application import export_loans, get_loan, list_loans


def loan_list(request):
    return HttpResponse(export_loans(list_loans()), content_type='text/plain')


def loan_detail(request, loan_id):
    loan = get_loan(loan_id)
    if loan is None:
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')
    return HttpResponse(f'{export_loans([loan])}', content_type='text/plain')


def ui_loan_list(request):
    loans = list(list_loans())
    return render(request, 'loans/list.html', {'loans': loans, 'loan_count': len(loans)})


def ui_loan_detail(request, loan_id):
    loan = get_loan(loan_id)
    if loan is None:
        raise Http404
    return render(request, 'loans/detail.html', {'loan': loan})
