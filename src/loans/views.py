from django.http import HttpResponse, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, render

from .composition import loan_application
from .models import Loan
from .services import (
    LoanAlreadyReturned,
    LoanInputError,
    LoanNotFound,
    get_loan_text,
    list_loans_text,
)


def loan_catalog(request):
    return render(request, 'loans/list.html', {'loans': loan_application().all()})


def loan_catalog_detail(request, loan_id):
    loan = get_object_or_404(Loan, pk=loan_id)
    return render(request, 'loans/detail.html', {'loan': loan})


def loan_list(request):
    if request.method == 'POST':
        if 'member' not in request.POST or 'isbn' not in request.POST:
            return HttpResponse(
                'member and isbn are required\n',
                status=400,
                content_type='text/plain',
            )
        application = loan_application()
        try:
            loan = application.lend(request.POST.get('member'), request.POST.get('isbn'))
        except LoanInputError as error:
            details = ''.join(f'{field}: {message}\n' for field, message in error.errors.items())
            return HttpResponse(details, status=400, content_type='text/plain')
        return HttpResponse(
            get_loan_text(loan),
            status=201,
            content_type='text/plain',
        )
    if request.method != 'GET':
        return HttpResponseNotAllowed(['GET', 'POST'])
    return HttpResponse(
        list_loans_text(loan_application().all()),
        content_type='text/plain',
    )


def loan_return(request, loan_id):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])
    try:
        loan = loan_application().return_loan(loan_id)
    except LoanNotFound:
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')
    except LoanAlreadyReturned:
        return HttpResponse('loan already returned\n', status=409, content_type='text/plain')
    return HttpResponse(get_loan_text(loan), content_type='text/plain')


def loan_detail(request, loan_id):
    body = get_loan_text(loan_application().find(loan_id))
    if body is None:
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')
    return HttpResponse(body, content_type='text/plain')
