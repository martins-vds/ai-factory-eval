from django.http import HttpResponse, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .models import Loan
from .repository import LoanRepository
from .services import (
    LoanAlreadyReturned,
    LoanInputError,
    LoanNotFound,
    get_loan_text,
    lend_loan,
    list_loans_text,
    loan_line,
    return_loan,
)


def loan_catalog(request):
    if request.method == 'POST':
        member = request.POST.get('member')
        isbn = request.POST.get('isbn')
        try:
            loan = lend_loan(
                repository=LoanRepository(),
                member=member,
                isbn=isbn,
                lent_on=timezone.localdate(),
            )
        except LoanInputError as error:
            context = {
                'errors': error.fields,
                'member': member or '',
                'isbn': isbn or '',
            }
            if request.headers.get('HX-Request') == 'true':
                return render(
                    request,
                    'loans/lend_form.html',
                    context,
                    status=400,
                )
            return render(request, 'loans/new.html', context, status=400)
        if request.headers.get('HX-Request') == 'true':
            return render(request, 'loans/lend_result.html', {'loan': loan})
        return redirect('/ui/loans/')
    if request.method != 'GET':
        return HttpResponseNotAllowed(['GET', 'POST'])
    return render(request, 'loans/list.html', {'loans': Loan.objects.all()})


def loan_lend_page(request):
    if request.method != 'GET':
        return HttpResponseNotAllowed(['GET'])
    return render(request, 'loans/new.html')


def loan_catalog_detail(request, loan_id):
    loan = get_object_or_404(Loan, pk=loan_id)
    return render(request, 'loans/detail.html', {'loan': loan})


def loan_list(request):
    if request.method == 'POST':
        try:
            loan = lend_loan(
                repository=LoanRepository(),
                member=request.POST.get('member'),
                isbn=request.POST.get('isbn'),
                lent_on=timezone.localdate(),
            )
        except LoanInputError:
            return HttpResponse(
                'member and isbn are required\n',
                status=400,
                content_type='text/plain',
            )
        return HttpResponse(
            loan_line(loan),
            status=201,
            content_type='text/plain',
        )
    if request.method != 'GET':
        return HttpResponseNotAllowed(['GET', 'POST'])
    return HttpResponse(
        list_loans_text(LoanRepository()),
        content_type='text/plain',
    )


def loan_detail(request, loan_id):
    body = get_loan_text(loan_id, LoanRepository())
    if body is None:
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')
    return HttpResponse(body, content_type='text/plain')


def loan_return(request, loan_id):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])
    try:
        loan = return_loan(
            repository=LoanRepository(),
            loan_id=loan_id,
            returned_on=timezone.localdate(),
        )
    except LoanNotFound:
        return HttpResponse(
            'no such loan\n',
            status=404,
            content_type='text/plain',
        )
    except LoanAlreadyReturned:
        return HttpResponse(
            'loan already returned\n',
            status=409,
            content_type='text/plain',
        )
    return HttpResponse(loan_line(loan), content_type='text/plain')


def loan_catalog_return(request, loan_id):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])
    try:
        loan = return_loan(
            repository=LoanRepository(),
            loan_id=loan_id,
            returned_on=timezone.localdate(),
        )
    except LoanNotFound:
        return render(
            request,
            'loans/return_status.html',
            {'error': 'No such loan.'},
            status=404,
        )
    except LoanAlreadyReturned:
        return render(
            request,
            'loans/return_status.html',
            {'error': 'This loan was already returned.'},
            status=409,
        )
    return render(request, 'loans/return_status.html', {'loan': loan})
