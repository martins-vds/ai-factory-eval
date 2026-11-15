from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods, require_POST

from .forms import LendLoanForm
from .models import Loan
from .services import get_loan_text, lend_loan, list_loans_text, loan_line, return_loan


def loan_catalog(request):
    return render(request, 'loans/list.html', {'loans': Loan.objects.all()})


def loan_catalog_detail(request, loan_id):
    loan = get_object_or_404(Loan, pk=loan_id)
    return render(request, 'loans/detail.html', {'loan': loan})


@require_http_methods(['GET', 'POST'])
def loan_list(request):
    if request.method == 'POST':
        return loan_lend(request)
    return HttpResponse(list_loans_text(), content_type='text/plain')


def loan_detail(request, loan_id):
    body = get_loan_text(loan_id)
    if body is None:
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')
    return HttpResponse(body, content_type='text/plain')


@require_POST
def loan_lend(request):
    form = LendLoanForm(request.POST)
    if not form.is_valid():
        return HttpResponse(
            'member and isbn are required\n',
            status=400,
            content_type='text/plain',
        )
    loan = lend_loan(**form.cleaned_data)
    return HttpResponse(loan_line(loan), status=201, content_type='text/plain')


@require_POST
def loan_return(request, loan_id):
    loan, changed = return_loan(loan_id)
    if loan is None:
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')
    if not changed:
        return HttpResponse('loan already returned\n', status=409, content_type='text/plain')
    return HttpResponse(loan_line(loan), content_type='text/plain')


def loan_lend_page(request):
    form = LendLoanForm(request.POST if request.method == 'POST' else None)
    if request.method == 'POST' and form.is_valid():
        lend_loan(**form.cleaned_data)
        if request.headers.get('HX-Request') == 'true':
            response = HttpResponse(status=204)
            response['HX-Redirect'] = '/ui/loans/'
            return response
        return redirect('/ui/loans/')

    context = {'form': form}
    if request.method == 'POST' and request.headers.get('HX-Request') == 'true':
        return render(request, 'loans/_lend_form.html', context)
    return render(request, 'loans/new.html', context)


@require_POST
def loan_return_page(request, loan_id):
    loan, changed = return_loan(loan_id)
    if loan is None:
        return HttpResponse('No such loan.', status=404)
    feedback = (
        f'{loan.id} marked returned today.'
        if changed
        else f'{loan.id} was already returned on {loan.returned_on}; repeat return rejected.'
    )
    if request.headers.get('HX-Request') == 'true':
        return render(request, 'loans/_loan_row.html', {'loan': loan, 'feedback': feedback})
    if not changed:
        return render(
            request,
            'loans/return_conflict.html',
            {'loan': loan},
            status=409,
        )
    return redirect('/ui/loans/')
