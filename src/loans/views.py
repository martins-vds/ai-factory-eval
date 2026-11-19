from django.http import HttpResponse, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .models import Loan
from .repository import LoanRepository
from .services import (
    LoanAlreadyReturned,
    LoanInputError,
    get_loan_text,
    lend_loan,
    list_loans_text,
    loan_line,
)
from .services import (
    return_loan as return_loan_use_case,
)


def loan_catalog(request):
    return render(request, 'loans/list.html', {'loans': Loan.objects.all()})


def loan_catalog_detail(request, loan_id):
    loan = get_object_or_404(Loan, pk=loan_id)
    return render(request, 'loans/detail.html', {'loan': loan})


def loan_list(request):
    if request.method == 'GET':
        return HttpResponse(
            list_loans_text(LoanRepository()),
            content_type='text/plain',
        )
    if request.method != 'POST':
        return HttpResponseNotAllowed(['GET', 'POST'])
    try:
        loan = lend_loan(
            LoanRepository(),
            request.POST.get('member'),
            request.POST.get('isbn'),
            timezone.localdate(),
        )
    except LoanInputError:
        return HttpResponse(
            'member and isbn are required\n',
            status=400,
            content_type='text/plain',
        )
    return HttpResponse(loan_line(loan), status=201, content_type='text/plain')


def loan_detail(request, loan_id):
    body = get_loan_text(LoanRepository(), loan_id)
    if body is None:
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')
    return HttpResponse(body, content_type='text/plain')


def loan_return(request, loan_id):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])
    try:
        loan = return_loan_use_case(LoanRepository(), loan_id, timezone.localdate())
    except LoanAlreadyReturned:
        return HttpResponse(
            'loan has already been returned\n',
            status=409,
            content_type='text/plain',
        )
    if loan is None:
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')
    return HttpResponse(loan_line(loan), content_type='text/plain')


def loan_lend_page(request):
    values = {'member': '', 'isbn': ''}
    errors = {}
    if request.method == 'POST':
        values = {
            'member': request.POST.get('member', ''),
            'isbn': request.POST.get('isbn', ''),
        }
        try:
            loan = lend_loan(
                LoanRepository(),
                values['member'],
                values['isbn'],
                timezone.localdate(),
            )
        except LoanInputError as error:
            errors = error.fields
        else:
            if request.headers.get('HX-Request') == 'true':
                return render(request, 'loans/partials/loan_created.html', {'loan': loan})
            return redirect('loan_catalog_detail', loan_id=loan.id)
    context = {'values': values, 'errors': errors}
    if request.headers.get('HX-Request') == 'true':
        return render(request, 'loans/partials/lend_form.html', context)
    return render(request, 'loans/new.html', context)


def loan_return_page(request, loan_id):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])
    try:
        loan = return_loan_use_case(LoanRepository(), loan_id, timezone.localdate())
    except LoanAlreadyReturned:
        return render(
            request,
            'loans/partials/return_status.html',
            {'message': 'This book has already been returned.', 'loan': None},
            status=409,
        )
    if loan is None:
        return render(
            request,
            'loans/partials/return_status.html',
            {'message': 'No such loan.', 'loan': None},
            status=404,
        )
    return render(request, 'loans/partials/return_status.html', {'message': '', 'loan': loan})
