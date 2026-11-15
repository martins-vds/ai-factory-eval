from django.http import HttpResponse, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods, require_POST

from .forms import LendLoanForm
from .models import Loan
from .services import get_loan_text, lend_loan, list_loans_text, loan_line, return_loan


def loan_catalog(request):
    return render(request, 'loans/list.html', {'loans': Loan.objects.all()})


def loan_catalog_detail(request, loan_id):
    loan = get_object_or_404(Loan, pk=loan_id)
    return render(request, 'loans/detail.html', {'loan': loan})


def loan_lend(request):
    if request.method not in ('GET', 'POST'):
        return HttpResponseNotAllowed(['GET', 'POST'])
    form = LendLoanForm(request.POST if request.method == 'POST' else None)
    if request.method == 'POST':
        if form.is_valid():
            lend_loan(**form.cleaned_data)
            if request.headers.get('HX-Request') == 'true':
                return HttpResponse(status=204, headers={'HX-Redirect': reverse('loan-catalog')})
            return redirect('loan-catalog')
        if request.headers.get('HX-Request') == 'true':
            return render(request, 'loans/_lend_form.html', {'form': form})
        return render(request, 'loans/new.html', {'form': form}, status=400)
    return render(request, 'loans/new.html', {'form': form})


def loan_catalog_return(request, loan_id):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])
    loan, returned = return_loan(loan_id)
    if loan is None:
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')
    if not returned:
        response = render(
            request,
            'loans/_loan_row.html',
            {'loan': loan, 'error': 'This book has already been returned.'},
            status=409,
        )
        response['HX-Retarget'] = f'#loan-{loan.pk}'
        response['HX-Reswap'] = 'outerHTML'
        return response
    if request.headers.get('HX-Request') == 'true':
        return render(request, 'loans/_loan_row.html', {'loan': loan})
    return redirect('loan-catalog')


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
    loan, returned = return_loan(loan_id)
    if loan is None:
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')
    if not returned:
        return HttpResponse('loan already returned\n', status=409, content_type='text/plain')
    return HttpResponse(loan_line(loan), content_type='text/plain')
