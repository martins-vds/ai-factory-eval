from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from .forms import LendLoanForm
from .models import Loan
from .services import get_loan_text, lend_loan, list_loans_text, loan_line, return_loan


def no_such_loan_response():
    return HttpResponse('no such loan\n', status=404, content_type='text/plain')


def loan_catalog(request):
    return render(request, 'loans/list.html', {'loans': Loan.objects.all()})


def loan_catalog_lend(request):
    form = LendLoanForm(request.POST if request.method == 'POST' else None)
    if request.method == 'POST':
        if form.is_valid():
            loan = lend_loan(**form.cleaned_data)
            if request.headers.get('HX-Request') == 'true':
                return render(request, 'loans/_lend_success.html', {'loan': loan})
            return redirect('/ui/loans/')
        if request.headers.get('HX-Request') == 'true':
            return render(request, 'loans/_lend_errors.html', {'form': form})
    return render(request, 'loans/new.html', {'form': form})


@require_http_methods(['POST'])
def loan_catalog_return(request, loan_id):
    loan, returned = return_loan(loan_id)
    if loan is None:
        return no_such_loan_response()
    if request.headers.get('HX-Request') == 'true':
        return render(
            request,
            'loans/_return_action.html',
            {
                'loan': loan,
                'error': None if returned else 'This loan has already been returned.',
            },
        )
    return redirect(f'/ui/loans/{loan.pk}/')


def loan_catalog_detail(request, loan_id):
    loan = get_object_or_404(Loan, pk=loan_id)
    return render(request, 'loans/detail.html', {'loan': loan})


@require_http_methods(['GET', 'POST'])
def loan_list(request):
    if request.method == 'POST':
        form = LendLoanForm(request.POST)
        if not form.is_valid():
            return HttpResponse(
                'member and isbn are required\n',
                status=400,
                content_type='text/plain',
            )
        return HttpResponse(
            loan_line(lend_loan(**form.cleaned_data)),
            status=201,
            content_type='text/plain',
        )
    return HttpResponse(list_loans_text(), content_type='text/plain')


def loan_detail(request, loan_id):
    body = get_loan_text(loan_id)
    if body is None:
        return no_such_loan_response()
    return HttpResponse(body, content_type='text/plain')


@require_http_methods(['POST'])
def loan_return(request, loan_id):
    loan, returned = return_loan(loan_id)
    if loan is None:
        return no_such_loan_response()
    if not returned:
        return HttpResponse(
            'loan has already been returned\n',
            status=409,
            content_type='text/plain',
        )
    return HttpResponse(loan_line(loan), content_type='text/plain')
