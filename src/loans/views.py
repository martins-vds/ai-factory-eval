from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods, require_POST

from .repository import LoanRepository
from .services import (
    AlreadyReturned,
    InvalidLoanInput,
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
    loan = get_loan(loan_id, LoanRepository())
    if loan is None:
        return HttpResponse('no such loan\n', status=404)
    return render(request, 'loans/detail.html', {'loan': loan})


def loan_list(request):
    return HttpResponse(list_loans_text(LoanRepository()), content_type='text/plain')


@require_http_methods(['GET', 'POST'])
def loan_collection(request):
    if request.method == 'POST':
        return loan_create(request)
    return loan_list(request)


def loan_detail(request, loan_id):
    body = get_loan_text(loan_id, LoanRepository())
    if body is None:
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')
    return HttpResponse(body, content_type='text/plain')


@require_POST
def loan_create(request):
    try:
        loan = lend_loan(
            request.POST.get('member'),
            request.POST.get('isbn'),
            LoanRepository(),
            timezone.localdate(),
        )
    except InvalidLoanInput:
        return HttpResponse('member and isbn are required\n', status=400, content_type='text/plain')
    return HttpResponse(loan_line(loan), status=201, content_type='text/plain')


@require_POST
def loan_return(request, loan_id):
    try:
        loan = return_loan(loan_id, LoanRepository(), timezone.localdate())
    except AlreadyReturned:
        return HttpResponse('loan already returned\n', status=409, content_type='text/plain')
    if loan is None:
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')
    return HttpResponse(loan_line(loan), content_type='text/plain')


@require_http_methods(['GET', 'POST'])
def loan_lend(request):
    if request.method == 'GET':
        return render(
            request,
            'loans/new.html',
            {'member': '', 'isbn': '', 'errors': {}},
        )

    member = request.POST.get('member')
    isbn = request.POST.get('isbn')
    try:
        loan = lend_loan(member, isbn, LoanRepository(), timezone.localdate())
    except InvalidLoanInput as error:
        context = {
            'member': member or '',
            'isbn': isbn or '',
            'errors': error.errors,
        }
        template = 'loans/_lend_form.html' if request.headers.get('HX-Request') == 'true' else 'loans/new.html'
        return render(request, template, context, status=422)

    if request.headers.get('HX-Request') == 'true':
        return render(request, 'loans/_lend_success.html', {'loan': loan}, status=201)
    return redirect('/ui/loans/')


@require_POST
def loan_return_ui(request, loan_id):
    repository = LoanRepository()
    try:
        loan = return_loan(loan_id, repository, timezone.localdate())
    except AlreadyReturned:
        return render(
            request,
            'loans/_loan_row.html',
            {'loan': get_loan(loan_id, repository), 'error': 'This loan has already been returned.'},
            status=409,
        )
    if loan is None:
        return render(request, 'loans/_return_feedback.html', {'error': 'No such loan.'}, status=404)
    return render(request, 'loans/_loan_row.html', {'loan': loan})
