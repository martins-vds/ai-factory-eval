from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods, require_POST

from .composition import loan_use_cases
from .forms import LoanForm
from .models import Loan
from .services import (
    InvalidLoan,
    LoanAlreadyReturned,
    get_loan_text,
    list_loans_text,
    loan_line,
)


@require_http_methods(['GET', 'POST'])
def loan_catalog(request):
    if request.method == 'POST':
        return loan_lend_page(request)
    return render(request, 'loans/list.html', {'loans': Loan.objects.all()})


def loan_catalog_detail(request, loan_id):
    loan = get_object_or_404(Loan, pk=loan_id)
    return render(request, 'loans/detail.html', {'loan': loan})


@require_http_methods(['GET', 'POST'])
def loan_list(request):
    use_cases = loan_use_cases()
    if request.method == 'POST':
        form = LoanForm(request.POST)
        if not form.is_valid():
            return HttpResponse(
                'member and isbn are required\n', status=400, content_type='text/plain'
            )
        loan = use_cases.lend(**form.cleaned_data)
        return HttpResponse(loan_line(loan), status=201, content_type='text/plain')
    return HttpResponse(list_loans_text(use_cases.all()), content_type='text/plain')


@require_http_methods(['GET', 'POST'])
def loan_lend_page(request):
    form = LoanForm(request.POST if request.method == 'POST' else None)
    if request.method == 'POST' and form.is_valid():
        try:
            loan = loan_use_cases().lend(**form.cleaned_data)
        except InvalidLoan as error:
            for field, message in error.fields.items():
                form.add_error(field, message)
        else:
            if request.headers.get('HX-Request') == 'true':
                return render(request, 'loans/loan-created.html', {'loan': loan}, status=201)
            return redirect(f'/ui/loans/{loan.id}/')
    template = (
        'loans/loan-form.html'
        if request.method == 'POST' and request.headers.get('HX-Request') == 'true'
        else 'loans/new.html'
    )
    return render(request, template, {'form': form})


def loan_detail(request, loan_id):
    body = get_loan_text(loan_use_cases().find(loan_id))
    if body is None:
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')
    return HttpResponse(body, content_type='text/plain')


@require_POST
def loan_return(request, loan_id):
    use_cases = loan_use_cases()
    try:
        loan = use_cases.return_loan(loan_id)
    except LoanAlreadyReturned:
        return HttpResponse('already returned\n', status=409, content_type='text/plain')
    if loan is None:
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')
    return HttpResponse(loan_line(loan), content_type='text/plain')


@require_POST
def loan_return_page(request, loan_id):
    use_cases = loan_use_cases()
    try:
        loan = use_cases.return_loan(loan_id)
    except LoanAlreadyReturned as error:
        loan = error.loan
        if request.headers.get('HX-Request') == 'true':
            return render(request, 'loans/return-status.html', {'loan': loan, 'updated': False})
        return render(
            request, 'loans/detail.html', {'loan': loan, 'return_error': True}, status=409
        )

    if loan is None:
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')

    if request.headers.get('HX-Request') == 'true':
        return render(request, 'loans/return-status.html', {'loan': loan, 'updated': True})
    return redirect(f'/ui/loans/{loan.id}/')
