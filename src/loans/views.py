from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_GET, require_http_methods, require_POST

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


@require_http_methods(['GET', 'POST'])
def loan_catalog(request):
    if request.method == 'POST':
        return loan_catalog_lend(request)
    return render(request, 'loans/list.html', {'loans': Loan.objects.all()})


@require_POST
def loan_catalog_lend(request):
    try:
        lend_loan(
            LoanRepository(),
            request.POST.get('member'),
            request.POST.get('isbn'),
            timezone.localdate(),
        )
    except LoanInputError as error:
        return render(
            request,
            'loans/new.html',
            {
                'form_values': {
                    'member': request.POST.get('member') or '',
                    'isbn': request.POST.get('isbn') or '',
                },
                'errors': error.errors,
            },
            status=400,
        )
    return redirect('/ui/loans/')


@require_GET
def loan_catalog_new(request):
    return render(
        request,
        'loans/new.html',
        {'form_values': {'member': '', 'isbn': ''}, 'errors': {}},
    )


def loan_catalog_detail(request, loan_id):
    loan = get_object_or_404(Loan, pk=loan_id)
    return render(request, 'loans/detail.html', {'loan': loan})


@require_POST
def loan_catalog_return(request, loan_id):
    repository = LoanRepository()
    try:
        loan = return_loan(repository, loan_id, timezone.localdate())
    except LoanNotFound:
        return render(
            request,
            'loans/return_status.html',
            {'loan': None, 'error': 'No such loan.'},
            status=404,
        )
    except LoanAlreadyReturned:
        return render(
            request,
            'loans/return_status.html',
            {'loan': repository.find(loan_id), 'error': 'This loan has already been returned.'},
            status=409,
        )
    return render(request, 'loans/return_status.html', {'loan': loan, 'error': ''})


@require_http_methods(['GET', 'POST'])
def loan_list(request):
    if request.method == 'POST':
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

    return HttpResponse(list_loans_text(LoanRepository()), content_type='text/plain')


def loan_detail(request, loan_id):
    body = get_loan_text(LoanRepository(), loan_id)
    if body is None:
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')
    return HttpResponse(body, content_type='text/plain')


@require_POST
def loan_return(request, loan_id):
    try:
        loan = return_loan(LoanRepository(), loan_id, timezone.localdate())
    except LoanNotFound:
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')
    except LoanAlreadyReturned:
        return HttpResponse('loan already returned\n', status=409, content_type='text/plain')
    return HttpResponse(loan_line(loan), content_type='text/plain')
