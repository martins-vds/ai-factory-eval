from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import LoanLendForm
from .models import Loan
from .services import get_loan_text, lend_book, list_loans_text, loan_line, return_book


def loan_catalog(request):
    return render(request, 'loans/list.html', {'loans': Loan.objects.all()})


def loan_catalog_detail(request, loan_id):
    loan = get_object_or_404(Loan, pk=loan_id)
    return render(request, 'loans/detail.html', {'loan': loan})


def loan_lend_ui(request):
    form = LoanLendForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        lend_book(**form.cleaned_data)
        return redirect('/ui/loans/')
    return render(request, 'loans/new.html', {'form': form})


def loan_list(request):
    if request.method == 'POST':
        form = LoanLendForm(request.POST)
        if not form.is_valid():
            return HttpResponse(
                'member and isbn are required\n',
                status=400,
                content_type='text/plain',
            )
        loan = lend_book(**form.cleaned_data)
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


def loan_return(request, loan_id):
    if request.method != 'POST':
        return HttpResponse(status=405)

    loan = return_book(loan_id)
    if loan is None:
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')
    if loan is False:
        return HttpResponse(
            'loan already returned\n',
            status=409,
            content_type='text/plain',
        )
    return HttpResponse(loan_line(loan), content_type='text/plain')
