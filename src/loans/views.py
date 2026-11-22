from django.http import HttpResponse, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .models import Loan
from .repository import LoanRepository
from .services import (
    LoanAlreadyReturned,
    LoanNotFound,
    LoanValidationError,
    get_loan_text,
    lend_book,
    list_loans_text,
    loan_line,
    return_book,
)


def loan_catalog(request):
    return render(request, 'loans/list.html', {'loans': Loan.objects.all()})


def loan_catalog_detail(request, loan_id):
    loan = get_object_or_404(Loan, pk=loan_id)
    return render(request, 'loans/detail.html', {'loan': loan})


def loan_lend_page(request):
    if request.method == 'GET':
        return render(request, 'loans/new.html')
    if request.method != 'POST':
        return HttpResponseNotAllowed(['GET', 'POST'])

    member = request.POST.get('member')
    isbn = request.POST.get('isbn')
    try:
        loan = lend_book(LoanRepository(), timezone.localdate(), member, isbn)
    except LoanValidationError as error:
        context = {
            'errors': error.errors,
            'member': member or '',
            'isbn': isbn or '',
        }
        template = (
            'loans/_lend_form.html'
            if request.headers.get('HX-Request') == 'true'
            else 'loans/new.html'
        )
        return render(request, template, context, status=400)

    if request.headers.get('HX-Request') == 'true':
        response = HttpResponse(status=204)
        response['HX-Redirect'] = f'/ui/loans/{loan.id}/'
        return response
    return redirect(f'/ui/loans/{loan.id}/')


def loan_catalog_return(request, loan_id):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])
    try:
        loan = return_book(LoanRepository(), loan_id, timezone.localdate())
    except LoanNotFound:
        return render_ui_return_error(request, 'No such loan.', 404)
    except LoanAlreadyReturned:
        return render_ui_return_error(request, 'This loan has already been returned.', 409)

    if request.headers.get('HX-Request') == 'true':
        response = HttpResponse(status=204)
        response['HX-Redirect'] = f'/ui/loans/{loan.id}/'
        return response
    return redirect(f'/ui/loans/{loan.id}/')


def render_ui_return_error(request, message, status):
    template = (
        'loans/_return_error.html'
        if request.headers.get('HX-Request') == 'true'
        else 'loans/return_error.html'
    )
    return render(request, template, {'message': message}, status=status)


def loan_list(request):
    repository = LoanRepository()
    if request.method == 'POST':
        try:
            loan = lend_book(
                repository,
                timezone.localdate(),
                request.POST.get('member'),
                request.POST.get('isbn'),
            )
        except LoanValidationError:
            return HttpResponse(
                'member and isbn are required\n', status=400, content_type='text/plain'
            )
        return HttpResponse(loan_line(loan), status=201, content_type='text/plain')
    if request.method == 'GET':
        return HttpResponse(list_loans_text(repository), content_type='text/plain')
    return HttpResponseNotAllowed(['GET', 'POST'])


def loan_detail(request, loan_id):
    if request.method != 'GET':
        return HttpResponseNotAllowed(['GET'])
    body = get_loan_text(LoanRepository(), loan_id)
    if body is None:
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')
    return HttpResponse(body, content_type='text/plain')


def loan_return(request, loan_id):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])
    try:
        loan = return_book(LoanRepository(), loan_id, timezone.localdate())
    except LoanNotFound:
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')
    except LoanAlreadyReturned:
        return HttpResponse('loan is already returned\n', status=409, content_type='text/plain')
    return HttpResponse(loan_line(loan), content_type='text/plain')
