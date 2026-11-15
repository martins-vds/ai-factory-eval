from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import LoanForm
from .models import Loan
from .repository import AlreadyReturnedError
from .services import get_loan_text, lend_book, list_loans_text, loan_line, return_book


def loan_catalog(request):
    return render(request, 'loans/list.html', {'loans': Loan.objects.all()})


def loan_catalog_detail(request, loan_id):
    loan = get_object_or_404(Loan, pk=loan_id)
    return render(request, 'loans/detail.html', {'loan': loan})


def loan_create_page(request):
    form = LoanForm(request.POST if request.method == 'POST' else None)
    if request.method == 'POST' and form.is_valid():
        loan = lend_book(**form.cleaned_data)
        if request.headers.get('HX-Request') == 'true':
            return render(request, 'loans/_loan_created.html', {'loan': loan})
        return redirect('loan_catalog_detail', loan_id=loan.id)
    if request.headers.get('HX-Request') == 'true':
        return render(request, 'loans/_loan_form.html', {'form': form})
    return render(request, 'loans/new.html', {'form': form})


@require_POST
def loan_return_page(request, loan_id):
    already_returned = False
    try:
        loan = return_book(loan_id)
    except AlreadyReturnedError:
        loan = get_object_or_404(Loan, pk=loan_id)
        already_returned = True
    if loan is None:
        return HttpResponseNotFound('no such loan\n', content_type='text/plain')
    if request.headers.get('HX-Request') == 'true':
        return render(
            request,
            'loans/_return_status.html',
            {'loan': loan, 'already_returned': already_returned},
        )
    return redirect('loan_catalog_detail', loan_id=loan.id)


def loan_list(request):
    if request.method == 'POST':
        return loan_lend(request)
    return HttpResponse(list_loans_text(), content_type='text/plain')


@require_POST
def loan_lend(request):
    form = LoanForm(request.POST)
    if not form.is_valid():
        return HttpResponse(
            'member and isbn are required\n',
            status=400,
            content_type='text/plain',
        )
    loan = lend_book(**form.cleaned_data)
    return HttpResponse(loan_line(loan), status=201, content_type='text/plain')


def loan_detail(request, loan_id):
    body = get_loan_text(loan_id)
    if body is None:
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')
    return HttpResponse(body, content_type='text/plain')


@require_POST
def loan_return(request, loan_id):
    try:
        loan = return_book(loan_id)
    except AlreadyReturnedError:
        return HttpResponse(
            'loan already returned\n',
            status=409,
            content_type='text/plain',
        )
    if loan is None:
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')
    return HttpResponse(loan_line(loan), content_type='text/plain')
