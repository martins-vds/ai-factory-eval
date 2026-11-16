from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods, require_POST

from .forms import LoanForm
from .models import Loan
from .services import (
    get_loan_text,
    lend_loan,
    list_loans_text,
    loan_line,
    mark_loan_returned,
)


def loan_catalog(request):
    return render(request, 'loans/list.html', {'loans': Loan.objects.all()})


@require_http_methods(['GET', 'POST'])
def loan_catalog_new(request):
    form = LoanForm(request.POST if request.method == 'POST' else None)
    if request.method == 'POST':
        if form.is_valid():
            lend_loan(**form.cleaned_data, lent_on=timezone.localdate())
            return redirect('/ui/loans/')
        return render(request, 'loans/new.html', {'form': form}, status=400)
    return render(request, 'loans/new.html', {'form': form})


def loan_catalog_detail(request, loan_id):
    loan = get_object_or_404(Loan, pk=loan_id)
    return render(request, 'loans/detail.html', {'loan': loan})


@require_http_methods(['GET', 'POST'])
def loan_list(request):
    if request.method == 'POST':
        if 'member' not in request.POST or 'isbn' not in request.POST:
            return HttpResponse(
                'member and isbn are required\n',
                status=400,
                content_type='text/plain',
            )
        form = LoanForm(request.POST)
        if not form.is_valid():
            errors = ''.join(
                f'{field}: {form.errors[field][0]}\n'
                for field in ('member', 'isbn')
                if field in form.errors
            )
            return HttpResponse(errors, status=400, content_type='text/plain')
        loan = lend_loan(**form.cleaned_data, lent_on=timezone.localdate())
        return HttpResponse(loan_line(loan), status=201, content_type='text/plain')
    return HttpResponse(list_loans_text(), content_type='text/plain')


def loan_detail(request, loan_id):
    body = get_loan_text(loan_id)
    if body is None:
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')
    return HttpResponse(body, content_type='text/plain')


@require_POST
def loan_return(request, loan_id):
    loan, updated = mark_loan_returned(loan_id, timezone.localdate())
    if loan is None:
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')
    if not updated:
        return HttpResponse('loan already returned\n', status=409, content_type='text/plain')
    return HttpResponse(loan_line(loan), content_type='text/plain')


@require_POST
def loan_catalog_return(request, loan_id):
    loan, updated = mark_loan_returned(loan_id, timezone.localdate())
    if loan is None:
        raise Http404
    if not updated:
        return render(
            request,
            'loans/list.html',
            {'loans': Loan.objects.all(), 'feedback': 'This loan has already been returned.'},
            status=409,
        )
    return redirect('/ui/loans/')
