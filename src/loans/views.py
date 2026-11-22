from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods, require_POST

from .composition import loan_repository, system_clock
from .forms import LoanForm
from .models import Loan
from .services import (
    LoanAlreadyReturned,
    LoanInputError,
    LoanNotFound,
    get_loan_text,
    lend_book,
    list_loans_text,
    loan_line,
    return_book,
)


def loan_catalog(request):
    if request.method == 'POST':
        return lend_loan_ui(request)
    return render(request, 'loans/list.html', {'loans': Loan.objects.all()})


def loan_catalog_detail(request, loan_id):
    loan = get_object_or_404(Loan, pk=loan_id)
    return render(request, 'loans/detail.html', {'loan': loan})


@csrf_exempt
def loan_list(request):
    if request.method == 'POST':
        return loan_lend(request)
    return HttpResponse(list_loans_text(loan_repository()), content_type='text/plain')


def loan_detail(request, loan_id):
    body = get_loan_text(loan_id, loan_repository())
    if body is None:
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')
    return HttpResponse(body, content_type='text/plain')


def loan_lend(request):
    try:
        loan = lend_book(
            request.POST.get('member'),
            request.POST.get('isbn'),
            loan_repository(),
            system_clock(),
        )
    except LoanInputError:
        return HttpResponse(
            'member and isbn are required\n',
            status=400,
            content_type='text/plain',
        )
    return HttpResponse(loan_line(loan), status=201, content_type='text/plain')


@csrf_exempt
@require_POST
def loan_return(request, loan_id):
    try:
        loan = return_book(loan_id, loan_repository(), system_clock())
    except LoanNotFound:
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')
    except LoanAlreadyReturned:
        return HttpResponse('loan already returned\n', status=409, content_type='text/plain')
    return HttpResponse(loan_line(loan), content_type='text/plain')


@require_http_methods(['GET', 'POST'])
def loan_lend_form(request):
    if request.method == 'GET':
        return render(request, 'loans/new.html', {'form': LoanForm()})
    return lend_loan_ui(request)


def lend_loan_ui(request):
    form = LoanForm(request.POST)
    if form.is_valid():
        try:
            loan = lend_book(
                form.cleaned_data.get('member'),
                form.cleaned_data.get('isbn'),
                loan_repository(),
                system_clock(),
            )
        except LoanInputError as error:
            for field, message in error.field_errors.items():
                form.add_error(field, message)
        else:
            return redirect('loan-catalog-detail', loan_id=loan.id)

    return render(request, 'loans/new.html', {'form': form}, status=400)


@require_POST
def loan_catalog_return(request, loan_id):
    try:
        loan = return_book(loan_id, loan_repository(), system_clock())
    except LoanNotFound:
        return render(
            request,
            'loans/return-status.html',
            {'loan': None, 'error': 'No such loan.'},
            status=404,
        )
    except LoanAlreadyReturned:
        loan = loan_repository().find(loan_id)
        return render(
            request,
            'loans/return-status.html',
            {'loan': loan, 'error': 'This loan has already been returned.'},
            status=409,
        )
    if request.headers.get('HX-Request') == 'true':
        return render(request, 'loans/return-status.html', {'loan': loan})
    return redirect('loan-catalog-detail', loan_id=loan.id)
