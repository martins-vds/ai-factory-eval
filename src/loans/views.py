from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods, require_POST

from .forms import LendLoanForm
from .models import Loan
from .services import get_loan_text, lend_loan, list_loans_text, loan_line, return_loan


@require_http_methods(['GET', 'POST'])
def loan_catalog(request):
    return render(request, 'loans/list.html', {'loans': Loan.objects.all()})


@require_http_methods(['GET', 'POST'])
def loan_lend(request):
    form = LendLoanForm(request.POST or None)
    if request.method == 'POST':
        if not form.is_valid():
            return render(request, 'loans/new.html', {'form': form}, status=400)
        lend_loan(**form.cleaned_data)
        return redirect('/ui/loans/')
    return render(request, 'loans/new.html', {'form': form})


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
        loan = lend_loan(**form.cleaned_data)
        return HttpResponse(loan_line(loan), status=201, content_type='text/plain')
    return HttpResponse(list_loans_text(), content_type='text/plain')


def loan_detail(request, loan_id):
    body = get_loan_text(loan_id)
    if body is None:
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')
    return HttpResponse(body, content_type='text/plain')


@require_POST
def loan_return(request, loan_id):
    result = return_loan(loan_id)
    if result is None:
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')
    loan, first_return = result
    if not first_return:
        return HttpResponse('loan already returned\n', status=409, content_type='text/plain')
    return HttpResponse(loan_line(loan), content_type='text/plain')


@require_POST
def loan_catalog_return(request, loan_id):
    result = return_loan(loan_id)
    if result is None:
        return HttpResponse('No such loan.', status=404)
    loan, first_return = result
    if not first_return:
        return render(
            request,
            'loans/detail.html',
            {'loan': loan, 'return_error': 'This book has already been returned.'},
            status=409,
        )
    return redirect('loan-detail-page', loan_id=loan_id)
