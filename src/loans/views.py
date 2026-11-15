from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods, require_POST

from .models import Loan
from .forms import LoanForm
from .services import get_loan_text, lend_loan, list_loans_text, loan_line, return_loan


@require_http_methods(['GET', 'POST'])
def loan_catalog(request):
    if request.method == 'POST':
        form = LoanForm(request.POST)
        if not form.is_valid():
            return render(request, 'loans/new.html', {'form': form}, status=400)
        lend_loan(**form.cleaned_data)
        return redirect('/ui/loans/')
    return render(request, 'loans/list.html', {'loans': Loan.objects.all()})


def loan_new(request):
    return render(request, 'loans/new.html', {'form': LoanForm()})


def loan_catalog_detail(request, loan_id):
    loan = get_object_or_404(Loan, pk=loan_id)
    return render(request, 'loans/detail.html', {'loan': loan})


@require_http_methods(['GET', 'POST'])
def loan_list(request):
    if request.method == 'POST':
        form = LoanForm(request.POST)
        if not form.is_valid():
            return HttpResponse(form.errors.as_text(), status=400, content_type='text/plain')
        loan = lend_loan(**form.cleaned_data)
        return HttpResponse(
            get_loan_text(loan.id),
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
    loan, updated = return_loan(loan_id)
    if loan is None:
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')
    if not updated:
        return HttpResponse('already returned\n', status=409, content_type='text/plain')
    return HttpResponse(loan_line(loan), content_type='text/plain')


@require_POST
def loan_catalog_return(request, loan_id):
    loan, updated = return_loan(loan_id)
    if loan is None:
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')
    feedback = None
    if not updated:
        feedback = (
            f'{loan.id} was already returned on {loan.returned_on}; '
            'repeat return rejected and original date retained.'
        )
    return render(request, 'loans/_row.html', {'loan': loan, 'feedback': feedback})
