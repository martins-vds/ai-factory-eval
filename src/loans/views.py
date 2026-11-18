from django.http import HttpResponse, HttpResponseNotAllowed
from django.shortcuts import redirect, render

from .clock import SystemClock
from .repository import LoanRepository
from .services import (
    LoanAlreadyReturned,
    LoanInputError,
    LoanNotFound,
    get_loan,
    get_loan_text,
    lend_loan,
    list_loans,
    list_loans_text,
    loan_line,
    return_loan,
)


def loan_catalog(request):
    return render(request, 'loans/list.html', {'loans': list_loans(LoanRepository())})


def loan_catalog_detail(request, loan_id):
    try:
        loan = get_loan(loan_id, LoanRepository())
    except LoanNotFound:
        return render(request, 'loans/not_found.html', status=404)
    return render(request, 'loans/detail.html', {'loan': loan})


def loan_lend_page(request):
    if request.method == 'GET':
        return render(
            request,
            'loans/new.html',
            {'member': '', 'isbn': '', 'errors': {}},
        )
    if request.method != 'POST':
        return HttpResponseNotAllowed(['GET', 'POST'])
    try:
        loan = lend_loan(
            request.POST.get('member'),
            request.POST.get('isbn'),
            LoanRepository(),
            SystemClock(),
        )
    except LoanInputError as error:
        context = {
            'member': request.POST.get('member', ''),
            'isbn': request.POST.get('isbn', ''),
            'errors': error.field_errors,
        }
        template = (
            'loans/_lend_form.html'
            if request.headers.get('HX-Request') == 'true'
            else 'loans/new.html'
        )
        return render(request, template, context, status=400)
    if request.headers.get('HX-Request') == 'true':
        return render(request, 'loans/_lend_success.html', {'loan': loan}, status=201)
    return redirect(f'/ui/loans/{loan.id}/')


def loan_list(request):
    if request.method == 'POST':
        try:
            loan = lend_loan(
                request.POST.get('member'),
                request.POST.get('isbn'),
                LoanRepository(),
                SystemClock(),
            )
        except LoanInputError:
            return HttpResponse(
                'member and isbn are required\n',
                status=400,
                content_type='text/plain',
            )
        return HttpResponse(loan_line(loan), status=201, content_type='text/plain')
    if request.method != 'GET':
        return HttpResponseNotAllowed(['GET', 'POST'])
    return HttpResponse(list_loans_text(LoanRepository()), content_type='text/plain')


def loan_detail(request, loan_id):
    body = get_loan_text(loan_id, LoanRepository())
    if body is None:
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')
    return HttpResponse(body, content_type='text/plain')


def loan_return(request, loan_id):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])
    try:
        loan = return_loan(loan_id, LoanRepository(), SystemClock())
    except LoanNotFound:
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')
    except LoanAlreadyReturned:
        return HttpResponse('loan already returned\n', status=409, content_type='text/plain')
    return HttpResponse(loan_line(loan), content_type='text/plain')


def loan_return_page(request, loan_id):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])
    is_htmx = request.headers.get('HX-Request') == 'true'
    try:
        loan = return_loan(loan_id, LoanRepository(), SystemClock())
    except LoanNotFound:
        if is_htmx:
            return render(
                request,
                'loans/_return_status.html',
                {'error': 'No such loan.'},
                status=404,
            )
        return render(request, 'loans/not_found.html', status=404)
    except LoanAlreadyReturned:
        if is_htmx:
            return render(
                request,
                'loans/_return_status.html',
                {'error': 'This loan has already been returned.'},
                status=409,
            )
        loan = LoanRepository().find(loan_id)
        return render(
            request,
            'loans/detail.html',
            {'loan': loan, 'return_error': 'This loan has already been returned.'},
            status=409,
        )
    if is_htmx:
        return render(request, 'loans/_return_status.html', {'loan': loan})
    return redirect(f'/ui/loans/{loan.id}/')
