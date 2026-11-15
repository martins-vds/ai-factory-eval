from datetime import date

from django.contrib import messages
from django.http import HttpResponse, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .forms import LendLoanForm
from .models import Loan
from .repository import LoanRepository
from .services import get_loan_text, list_loans_text, loan_line


def loan_catalog(request):
    return render(request, 'loans/list.html', {'loans': Loan.objects.all()})


def loan_catalog_detail(request, loan_id):
    loan = get_object_or_404(Loan, pk=loan_id)
    return render(request, 'loans/detail.html', {'loan': loan})


def loan_lend_ui(request):
    form = LendLoanForm(request.POST if request.method == 'POST' else None)
    if request.method == 'POST':
        if not form.is_valid():
            return render(request, 'loans/new.html', {'form': form})
        loan = LoanRepository().lend(**form.cleaned_data)
        messages.success(request, f'Loan {loan.id} added to the collection.')
        destination = reverse('loan_catalog')
        return _ui_redirect(request, destination)
    if request.method != 'GET':
        return HttpResponseNotAllowed(['GET', 'POST'])
    return render(request, 'loans/new.html', {'form': form})


def loan_catalog_return(request, loan_id):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])
    loan, updated = LoanRepository().mark_returned(loan_id, date.today())
    if loan is None:
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')
    if updated:
        messages.success(request, f'Loan {loan.id} marked returned today.')
    else:
        messages.warning(
            request,
            f'{loan.id} was already returned; the original return date was retained.',
        )
    return _ui_redirect(request, reverse('loan_catalog_detail', args=[loan.id]))


def loan_list(request):
    if request.method == 'POST':
        form = LendLoanForm(request.POST)
        if not form.is_valid():
            return HttpResponse(
                'member and isbn are required\n',
                status=400,
                content_type='text/plain',
            )
        loan = LoanRepository().lend(**form.cleaned_data)
        return HttpResponse(loan_line(loan), status=201, content_type='text/plain')
    return HttpResponse(list_loans_text(), content_type='text/plain')


def loan_detail(request, loan_id):
    body = get_loan_text(loan_id)
    if body is None:
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')
    return HttpResponse(body, content_type='text/plain')


def loan_return(request, loan_id):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])
    loan, updated = LoanRepository().mark_returned(loan_id, date.today())
    if loan is None:
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')
    if not updated:
        return HttpResponse(
            'loan already returned\n',
            status=409,
            content_type='text/plain',
        )
    return HttpResponse(loan_line(loan), content_type='text/plain')


def _ui_redirect(request, destination):
    if request.headers.get('HX-Request') == 'true':
        return HttpResponse(status=204, headers={'HX-Redirect': destination})
    return redirect(destination)
