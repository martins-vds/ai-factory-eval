from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods, require_POST

from .forms import LoanLendForm
from .models import Loan
from .repository import LoanRepository
from .services import get_loan_text, lend_loan, list_loans_text, loan_line, return_loan


def loan_catalog(request, form=None, feedback=None, status=200):
    return render(
        request,
        'loans/list.html',
        {
            'loans': LoanRepository().all(),
            'form': form or LoanLendForm(),
            'feedback': feedback,
        },
        status=status,
    )


def loan_catalog_detail(request, loan_id):
    loan = get_object_or_404(Loan, pk=loan_id)
    return render(request, 'loans/detail.html', {'loan': loan})


@require_http_methods(['GET', 'POST'])
def loan_list(request):
    if request.method == 'POST':
        return loan_lend(request)
    return HttpResponse(
        list_loans_text(LoanRepository()),
        content_type='text/plain',
    )


def loan_detail(request, loan_id):
    body = get_loan_text(LoanRepository(), loan_id)
    if body is None:
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')
    return HttpResponse(body, content_type='text/plain')


def loan_lend(request):
    form = LoanLendForm(request.POST or None)
    if request.method == 'GET':
        return loan_catalog(request, form=form)
    if not form.is_valid():
        return HttpResponse(
            'member and isbn are required\n',
            status=400,
            content_type='text/plain',
        )
    loan = lend_loan(
        LoanRepository(),
        **form.cleaned_data,
        lent_on=timezone.localdate(),
    )
    return HttpResponse(
        loan_line(loan),
        status=201,
        content_type='text/plain',
    )


@require_http_methods(['GET', 'POST'])
def loan_lend_browser(request):
    if request.method == 'GET':
        return loan_catalog(request)
    form = LoanLendForm(request.POST)
    if not form.is_valid():
        return loan_catalog(request, form=form)
    lend_loan(
        LoanRepository(),
        **form.cleaned_data,
        lent_on=timezone.localdate(),
    )
    if request.headers.get('HX-Request') == 'true':
        return loan_catalog(request, feedback='Loan created.')
    return redirect('/ui/loans/')


@require_POST
def loan_return(request, loan_id):
    result = return_loan(LoanRepository(), loan_id, timezone.localdate())
    if result is None:
        return HttpResponse(
            'no such loan\n',
            status=404,
            content_type='text/plain',
        )
    loan, updated = result
    if not updated:
        return HttpResponse(
            'loan already returned\n',
            status=409,
            content_type='text/plain',
        )
    return HttpResponse(
        loan_line(loan),
        content_type='text/plain',
    )


@require_POST
def loan_return_browser(request, loan_id):
    result = return_loan(LoanRepository(), loan_id, timezone.localdate())
    if result is None:
        return HttpResponse('no such loan\n', status=404)
    _, updated = result
    if updated:
        if request.headers.get('HX-Request') != 'true':
            return redirect('/ui/loans/')
        feedback = 'Loan returned.'
    else:
        feedback = 'This loan has already been returned.'
    return loan_catalog(request, feedback=feedback)
