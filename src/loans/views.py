from django.http import HttpResponse, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, render

from .models import Loan
from .services import get_loan_text, lend_loan, list_loans_text, loan_line


def loan_catalog(request):
    return render(request, 'loans/list.html', {'loans': Loan.objects.all()})


def loan_catalog_detail(request, loan_id):
    loan = get_object_or_404(Loan, pk=loan_id)
    return render(request, 'loans/detail.html', {'loan': loan})


def loan_list(request):
    return HttpResponse(list_loans_text(), content_type='text/plain')


def loan_collection(request):
    if request.method == 'GET':
        return loan_list(request)
    if request.method == 'POST':
        return loan_lend(request)
    return HttpResponseNotAllowed(['GET', 'POST'])


def loan_lend(request):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    loan = lend_loan(request.POST.get('member'), request.POST.get('isbn'))
    if loan is None:
        return HttpResponse(
            'member and isbn are required\n',
            status=400,
            content_type='text/plain',
        )
    return HttpResponse(loan_line(loan), status=201, content_type='text/plain')


def loan_detail(request, loan_id):
    body = get_loan_text(loan_id)
    if body is None:
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')
    return HttpResponse(body, content_type='text/plain')
