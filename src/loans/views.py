from datetime import date

from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from .models import Loan
from .repository import LoanRepository
from .services import (
    InvalidLoan,
    LoanAlreadyReturned,
    get_loan_text,
    lend_loan,
    list_loans_text,
    return_loan,
)


def _catalog_page(request, **context):
    page_context = {
        'loans': Loan.objects.all(),
        'form_values': {'member': '', 'isbn': ''},
        'errors': {},
        'feedback': '',
    }
    page_context.update(context)
    return render(request, 'loans/list.html', page_context, status=context.get('status', 200))


def _catalog_redirect(request):
    if request.headers.get('HX-Request') == 'true':
        return HttpResponse(status=204, headers={'HX-Redirect': '/ui/loans/'})
    return redirect('/ui/loans/')


@require_GET
def loan_catalog(request):
    return _catalog_page(request)


@require_GET
def loan_catalog_detail(request, loan_id):
    loan = get_object_or_404(Loan, pk=loan_id)
    return render(request, 'loans/detail.html', {'loan': loan})


@require_http_methods(['GET', 'POST'])
def loan_catalog_new(request):
    if request.method == 'GET':
        return _catalog_page(request)
    form_values = {
        'member': request.POST.get('member', ''),
        'isbn': request.POST.get('isbn', ''),
    }
    try:
        lend_loan(LoanRepository(), form_values['member'], form_values['isbn'], date.today())
    except InvalidLoan as error:
        return _catalog_page(request, form_values=form_values, errors=error.errors, status=400)
    return _catalog_redirect(request)


@require_POST
def loan_catalog_return(request, loan_id):
    try:
        loan = return_loan(LoanRepository(), loan_id, date.today())
    except LoanAlreadyReturned:
        return _catalog_page(
            request,
            feedback='This loan was already returned; the original date was kept.',
            status=409,
        )
    if loan is None:
        return _catalog_page(request, feedback='No such loan.', status=404)
    return _catalog_redirect(request)


@require_http_methods(['GET', 'POST'])
def loan_list(request):
    if request.method == 'POST':
        try:
            loan = lend_loan(
                LoanRepository(),
                request.POST.get('member'),
                request.POST.get('isbn'),
                date.today(),
            )
        except InvalidLoan:
            return HttpResponse('member and isbn are required\n', status=400, content_type='text/plain')
        return HttpResponse(
            get_loan_text(LoanRepository(), loan.id),
            status=201,
            content_type='text/plain',
        )
    return HttpResponse(list_loans_text(LoanRepository()), content_type='text/plain')


@require_GET
def loan_detail(request, loan_id):
    body = get_loan_text(LoanRepository(), loan_id)
    if body is None:
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')
    return HttpResponse(body, content_type='text/plain')


@require_POST
def loan_return(request, loan_id):
    try:
        loan = return_loan(LoanRepository(), loan_id, date.today())
    except LoanAlreadyReturned:
        return HttpResponse('loan already returned\n', status=409, content_type='text/plain')
    if loan is None:
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')
    return HttpResponse(get_loan_text(LoanRepository(), loan.id), content_type='text/plain')
