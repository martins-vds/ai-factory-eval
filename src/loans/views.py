from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods, require_POST

from .forms import LoanForm
from .models import Loan
from .services import get_loan_text, lend_book, list_loans_text, loan_line, return_book


def loan_catalog(request):
    return render(request, 'loans/list.html', {'loans': Loan.objects.all()})


def loan_catalog_detail(request, loan_id):
    loan = get_object_or_404(Loan, pk=loan_id)
    return render(request, 'loans/detail.html', {'loan': loan})


@require_http_methods(['GET', 'POST'])
def loan_catalog_new(request):
    if request.method == 'POST':
        form = LoanForm(request.POST)
        if form.is_valid():
            lend_book(**form.cleaned_data)
            if request.headers.get('HX-Request') == 'true':
                response = HttpResponse(status=200)
                response['HX-Redirect'] = '/ui/loans/'
                return response
            return redirect('/ui/loans/')
    else:
        form = LoanForm()
    return render(request, 'loans/new.html', {'form': form})


@require_POST
def loan_catalog_return(request, loan_id):
    loan, updated = return_book(loan_id)
    if loan is None:
        loan = get_object_or_404(Loan, pk=loan_id)
    if not updated:
        return render(
            request,
            'loans/detail.html',
            {'loan': loan, 'return_error': 'This loan has already been returned.'},
            status=409,
        )
    if request.headers.get('HX-Request') == 'true':
        response = HttpResponse(status=200)
        response['HX-Redirect'] = f'/ui/loans/{loan.id}/'
        return response
    return redirect(f'/ui/loans/{loan.id}/')


@csrf_exempt
def loan_list(request):
    if request.method == 'POST':
        form = LoanForm(request.POST)
        if not form.is_valid():
            return HttpResponse(
                'member and isbn are required\n',
                status=400,
                content_type='text/plain',
            )
        loan = lend_book(**form.cleaned_data)
        return HttpResponse(loan_line(loan), status=201, content_type='text/plain')
    return HttpResponse(list_loans_text(), content_type='text/plain')


@csrf_exempt
@require_POST
def loan_return(request, loan_id):
    loan, updated = return_book(loan_id)
    if loan is None:
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')
    if not updated:
        return HttpResponse(
            'loan already returned\n',
            status=409,
            content_type='text/plain',
        )
    return HttpResponse(loan_line(loan), content_type='text/plain')


def loan_detail(request, loan_id):
    body = get_loan_text(loan_id)
    if body is None:
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')
    return HttpResponse(body, content_type='text/plain')
