from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods, require_POST

from .forms import LoanLendForm
from .models import Loan
from .services import (
    get_loan_text,
    lend_loan,
    list_loans_text,
    loan_line,
    return_loan,
)


def loan_catalog(request):
    return render(request, 'loans/list.html', {'loans': Loan.objects.all()})


def loan_lend_page(request):
    form = LoanLendForm(request.POST if request.method == 'POST' else None)
    if request.method == 'POST' and form.is_valid():
        loan = lend_loan(form.cleaned_data['member'], form.cleaned_data['isbn'])
        return redirect('loan_catalog_detail', loan_id=loan.id)
    return render(request, 'loans/new.html', {'form': form})


def loan_catalog_detail(request, loan_id):
    loan = get_object_or_404(Loan, pk=loan_id)
    return render(request, 'loans/detail.html', {'loan': loan})


@require_POST
def loan_return_page(request, loan_id):
    loan, already_returned = return_loan(loan_id)
    if loan is None:
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')
    if already_returned:
        return render(
            request,
            'loans/detail.html',
            {'loan': loan, 'return_error': 'This loan has already been returned.'},
            status=409,
        )
    return redirect('loan_catalog_detail', loan_id=loan.id)


@require_http_methods(['GET', 'POST'])
def loan_list(request):
    if request.method == 'POST':
        form = LoanLendForm(request.POST)
        if not form.is_valid():
            return HttpResponse(
                'member and isbn are required\n',
                status=400,
                content_type='text/plain',
            )
        loan = lend_loan(form.cleaned_data['member'], form.cleaned_data['isbn'])
        return HttpResponse(
            loan_line(loan),
            status=201,
            content_type='text/plain',
        )
    return HttpResponse(list_loans_text(), content_type='text/plain')


def loan_detail(request, loan_id):
    body = get_loan_text(loan_id)
    if body is None:
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')
    return HttpResponse(body, content_type='text/plain')


@require_POST
def loan_return(request, loan_id):
    loan, already_returned = return_loan(loan_id)
    if loan is None:
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')
    if already_returned:
        return HttpResponse('loan already returned\n', status=409, content_type='text/plain')
    return HttpResponse(loan_line(loan), content_type='text/plain')
