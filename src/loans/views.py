from django.http import Http404, HttpResponse, HttpResponseNotAllowed
from django.shortcuts import render

from .composition import all_loans, find_loan, get_loan_text, give_back, lend, list_loans_text
from .services import LoanAlreadyReturned, LoanInputError, LoanNotFound, loan_line


def loan_catalog(request):
    return render(request, 'loans/list.html', {'loans': all_loans()})


def loan_catalog_detail(request, loan_id):
    loan = find_loan(loan_id)
    if loan is None:
        raise Http404('No such loan.')
    return render(request, 'loans/detail.html', {'loan': loan})


def loan_list(request):
    if request.method == 'POST':
        return loan_lend(request)
    if request.method != 'GET':
        return HttpResponseNotAllowed(['GET', 'POST'])
    return HttpResponse(list_loans_text(), content_type='text/plain')


def loan_detail(request, loan_id):
    body = get_loan_text(loan_id)
    if body is None:
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')
    return HttpResponse(body, content_type='text/plain')


def loan_lend(request):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])
    try:
        loan = lend(request.POST.get('member'), request.POST.get('isbn'))
    except LoanInputError:
        return HttpResponse(
            'member and isbn are required\n',
            status=400,
            content_type='text/plain',
        )
    return HttpResponse(loan_line(loan), status=201, content_type='text/plain')


def loan_return(request, loan_id):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])
    try:
        loan = give_back(loan_id)
    except LoanNotFound:
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')
    except LoanAlreadyReturned:
        return HttpResponse('loan already returned\n', status=409, content_type='text/plain')
    return HttpResponse(loan_line(loan), content_type='text/plain')
