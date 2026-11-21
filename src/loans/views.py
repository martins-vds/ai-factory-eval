from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .models import Loan
from .repository import LoanRepository
from .services import (
    LoanAlreadyReturnedError,
    LoanNotFoundError,
    RequiredLoanFieldError,
    get_loan_text,
    lend_loan,
    list_loans_text,
    return_loan,
)


def loan_catalog(request):
    return render(request, 'loans/list.html', {'loans': Loan.objects.all()})


def loan_catalog_detail(request, loan_id):
    loan = get_object_or_404(Loan, pk=loan_id)
    return render(request, 'loans/detail.html', {'loan': loan})


def loan_list(request):
    repository = LoanRepository()
    if request.method == 'POST':
        return loan_create(request)
    return HttpResponse(list_loans_text(repository), content_type='text/plain')


def loan_detail(request, loan_id):
    body = get_loan_text(loan_id, LoanRepository())
    if body is None:
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')
    return HttpResponse(body, content_type='text/plain')


def loan_create(request):
    if request.method != 'POST':
        return HttpResponse(status=405)
    repository = LoanRepository()
    try:
        loan = lend_loan(
            request.POST.get('member'),
            request.POST.get('isbn'),
            repository,
            timezone.localdate(),
        )
    except RequiredLoanFieldError:
        return HttpResponse('member and isbn are required\n', status=400, content_type='text/plain')
    body = get_loan_text(loan.id, repository)
    return HttpResponse(body, status=201, content_type='text/plain')


def loan_return(request, loan_id):
    if request.method != 'POST':
        return HttpResponse(status=405)
    repository = LoanRepository()
    try:
        loan = return_loan(loan_id, repository, timezone.localdate())
    except LoanNotFoundError:
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')
    except LoanAlreadyReturnedError:
        return HttpResponse('loan already returned\n', status=409, content_type='text/plain')
    body = get_loan_text(loan.id, repository)
    return HttpResponse(body, content_type='text/plain')


def loan_new(request):
    if request.method == 'POST':
        repository = LoanRepository()
        try:
            loan = lend_loan(
                request.POST.get('member'),
                request.POST.get('isbn'),
                repository,
                timezone.localdate(),
            )
        except RequiredLoanFieldError:
            return render(
                request,
                'loans/new.html',
                {
                    'error': 'Member and ISBN are required.',
                    'member': request.POST.get('member', ''),
                    'isbn': request.POST.get('isbn', ''),
                },
                status=400,
            )
        return redirect('loan_catalog_detail', loan_id=loan.id)
    return render(request, 'loans/new.html')


def loan_return_ui(request, loan_id):
    if request.method != 'POST':
        return HttpResponse(status=405)
    repository = LoanRepository()
    loan = repository.find(loan_id)
    if loan is None:
        return render(
            request, 'loans/detail.html', {'loan': None, 'error': 'Loan not found.'}, status=404
        )
    try:
        return_loan(loan_id, repository, timezone.localdate())
    except LoanAlreadyReturnedError:
        return render(
            request,
            'loans/detail.html',
            {'loan': loan, 'error': 'This loan has already been returned.'},
            status=409,
        )
    return redirect('loan_catalog_detail', loan_id=loan.id)
