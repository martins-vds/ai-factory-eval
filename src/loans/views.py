from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from .models import Loan
from .services import (
    get_loan_text,
    lend_book,
    list_loans_text,
    loan_line,
    return_loan,
)


def loan_catalog(request):
    return render(request, 'loans/list.html', {'loans': Loan.objects.all()})


def loan_catalog_detail(request, loan_id):
    loan = get_object_or_404(Loan, pk=loan_id)
    return render(request, 'loans/detail.html', {'loan': loan})


@require_http_methods(['GET', 'POST'])
def loan_new(request):
    if request.method == 'GET':
        return render(request, 'loans/new.html')

    member = request.POST.get('member', '')
    isbn = request.POST.get('isbn', '')
    errors = {'member': not member.strip(), 'isbn': not isbn.strip()}
    if any(errors.values()):
        return render(
            request,
            'loans/new.html',
            {'member': member, 'isbn': isbn, 'errors': errors},
        )

    loan = lend_book(member, isbn)
    if request.headers.get('HX-Request') == 'true':
        return render(request, 'loans/lend_success.html', {'loan': loan})
    return redirect(f'/ui/loans/{loan.id}/')


@require_http_methods(['POST'])
def loan_catalog_return(request, loan_id):
    loan, returned = return_loan(loan_id)
    if loan is None:
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')
    if request.headers.get('HX-Request') == 'true':
        return render(
            request,
            'loans/return_action.html',
            {'loan': loan, 'returned': returned},
        )
    return redirect(f'/ui/loans/{loan.id}/')


@require_http_methods(['GET', 'POST'])
def loan_list(request):
    if request.method == 'POST':
        member = request.POST.get('member')
        isbn = request.POST.get('isbn')
        if not member or not member.strip() or not isbn or not isbn.strip():
            return HttpResponse(
                'member and isbn are required\n',
                status=400,
                content_type='text/plain',
            )
        return HttpResponse(
            loan_line(lend_book(member, isbn)),
            status=201,
            content_type='text/plain',
        )
    return HttpResponse(list_loans_text(), content_type='text/plain')


def loan_detail(request, loan_id):
    body = get_loan_text(loan_id)
    if body is None:
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')
    return HttpResponse(body, content_type='text/plain')


@require_http_methods(['POST'])
def loan_return(request, loan_id):
    loan, returned = return_loan(loan_id)
    if loan is None:
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')
    if not returned:
        return HttpResponse('loan already returned\n', status=409, content_type='text/plain')
    return HttpResponse(loan_line(loan), content_type='text/plain')
