from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import LoanForm
from .models import Loan
from .services import get_loan_text, lend_loan, list_loans_text, loan_line, return_loan


def _return_error(status):
    message = 'no such loan\n' if status == 404 else 'loan already returned\n'
    return HttpResponse(message, status=status, content_type='text/plain')


def loan_catalog(request):
    return render(request, 'loans/list.html', {'loans': Loan.objects.all()})


def loan_catalog_detail(request, loan_id):
    loan = get_object_or_404(Loan, pk=loan_id)
    return render(request, 'loans/detail.html', {'loan': loan})


def loan_list(request):
    if request.method == 'POST':
        form = LoanForm(request.POST)
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


def loan_catalog_lend(request):
    form = LoanForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        loan = lend_loan(**form.cleaned_data)
        return redirect('loan_catalog_detail', loan_id=loan.id)
    return render(request, 'loans/new.html', {'form': form})


@require_POST
def loan_return(request, loan_id):
    result = return_loan(loan_id)
    if result is None:
        return _return_error(404)
    loan, returned_now = result
    if not returned_now:
        return _return_error(409)
    return HttpResponse(loan_line(loan), content_type='text/plain')


@require_POST
def loan_catalog_return(request, loan_id):
    result = return_loan(loan_id)
    if result is None:
        return _return_error(404)
    loan, returned_now = result
    if not returned_now:
        return _return_error(409)
    if request.headers.get('HX-Request') == 'true':
        return render(
            request,
            'loans/_loan_list.html',
            {'loans': Loan.objects.all()},
        )
    return redirect('loan_catalog_detail', loan_id=loan.id)
