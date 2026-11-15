from django.http import Http404, HttpResponse
from django.shortcuts import render

from .export import format_loan
from .repository import get_loan, list_loans


def loan_list(request):
    return HttpResponse(
        ''.join(format_loan(loan) for loan in list_loans()),
        content_type='text/plain',
    )


def loan_detail(request, loan_id):
    loan = get_loan(loan_id)
    if loan is None:
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')
    return HttpResponse(format_loan(loan), content_type='text/plain')


def catalog(request):
    return render(request, 'loans/catalog.html', {'loans': list_loans()})


def catalog_detail(request, loan_id):
    loan = get_loan(loan_id)
    if loan is None:
        raise Http404
    return render(request, 'loans/detail.html', {'loan': loan})
