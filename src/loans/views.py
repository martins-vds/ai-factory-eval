from django.http import HttpResponse, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, redirect, render

from .models import Loan
from .services import (
    get_loan_text,
    lend_loan,
    list_loans_text,
    loan_field_errors,
    loan_line,
    return_loan,
)


def loan_catalog(request):
    return _render_loan_catalog(request)


def loan_catalog_detail(request, loan_id):
    loan = get_object_or_404(Loan, pk=loan_id)
    return render(request, 'loans/detail.html', {'loan': loan})


def loan_lend_ui(request):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    member = request.POST.get('member', '')
    isbn = request.POST.get('isbn', '')
    errors = loan_field_errors(member, isbn)
    if errors:
        return _render_loan_catalog(
            request,
            errors=errors,
            form_data={'member': member, 'isbn': isbn},
            status=200 if _is_htmx(request) else 400,
        )
    lend_loan(member, isbn)
    if _is_htmx(request):
        return _render_loan_catalog(request)
    return redirect('/ui/loans/')


def loan_return_ui(request, loan_id):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    loan, updated = return_loan(loan_id)
    if loan is None:
        return _render_loan_catalog(
            request,
            error='No such loan.',
            status=404,
        )
    error = None if updated else 'This loan has already been returned.'
    return _render_loan_catalog(request, error=error)


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


def loan_return(request, loan_id):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    loan, updated = return_loan(loan_id)
    if loan is None:
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')
    if not updated:
        return HttpResponse(
            'loan already returned\n',
            status=409,
            content_type='text/plain',
        )
    return HttpResponse(loan_line(loan), content_type='text/plain')


def loan_detail(request, loan_id):
    body = get_loan_text(loan_id)
    if body is None:
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')
    return HttpResponse(body, content_type='text/plain')


def _is_htmx(request):
    return request.headers.get('HX-Request') == 'true'


def _render_loan_catalog(request, error=None, errors=None, form_data=None, status=200):
    template = 'loans/_library.html' if _is_htmx(request) else 'loans/list.html'
    return render(
        request,
        template,
        {
            'loans': Loan.objects.all(),
            'error': error,
            'errors': errors or {},
            'form_data': form_data or {},
        },
        status=status,
    )
