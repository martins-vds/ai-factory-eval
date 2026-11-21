from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods, require_POST

from .models import Loan
from .repository import LoanRepository
from .services import (
    LoanAlreadyReturned,
    LoanInputError,
    LoanNotFound,
    get_loan,
    get_loan_text,
    lend_loan,
    list_loans,
    list_loans_text,
    loan_line,
    return_loan,
)


def loan_catalog(request):
    return render(request, 'loans/list.html', {'loans': list_loans(LoanRepository())})


def loan_catalog_detail(request, loan_id):
    loan = get_object_or_404(Loan, pk=loan_id)
    return render(request, 'loans/detail.html', {'loan': loan})


@require_http_methods(['GET', 'POST'])
def loan_list(request):
    repository = LoanRepository()
    if request.method == 'POST':
        try:
            loan = lend_loan(repository, request.POST.get('member'), request.POST.get('isbn'))
        except LoanInputError:
            return HttpResponse(
                'member and isbn are required\n',
                status=400,
                content_type='text/plain',
            )
        return HttpResponse(loan_line(loan), status=201, content_type='text/plain')

    return HttpResponse(list_loans_text(repository), content_type='text/plain')


def loan_detail(request, loan_id):
    body = get_loan_text(LoanRepository(), loan_id)
    if body is None:
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')
    return HttpResponse(body, content_type='text/plain')


@require_POST
def loan_return(request, loan_id):
    try:
        loan = return_loan(loan_id, LoanRepository())
    except LoanNotFound:
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')
    except LoanAlreadyReturned:
        return HttpResponse('loan already returned\n', status=409, content_type='text/plain')
    return HttpResponse(loan_line(loan), content_type='text/plain')


@require_http_methods(['GET', 'POST'])
def loan_new(request):
    if request.method == 'GET':
        return render(request, 'loans/new.html')

    try:
        loan = lend_loan(
            LoanRepository(),
            request.POST.get('member'),
            request.POST.get('isbn'),
        )
    except LoanInputError as error:
        template = (
            'loans/_loan_form.html'
            if request.headers.get('HX-Request') == 'true'
            else 'loans/new.html'
        )
        return render(request, template, {'errors': error.errors}, status=422)

    location = reverse('loan_catalog_detail', kwargs={'loan_id': loan.id})
    if request.headers.get('HX-Request') == 'true':
        return HttpResponse(status=201, headers={'HX-Redirect': location})
    return redirect(location)


@require_POST
def loan_return_ui(request, loan_id):
    repository = LoanRepository()
    try:
        loan = return_loan(loan_id, repository)
    except LoanNotFound:
        return render(
            request,
            'loans/_return_status.html',
            {'error': 'no such loan'},
            status=404,
        )
    except LoanAlreadyReturned:
        return render(
            request,
            'loans/_return_status.html',
            {
                'error': 'loan already returned',
                'loan': get_loan(repository, loan_id),
            },
            status=409,
        )

    if request.headers.get('HX-Request') != 'true':
        return redirect('loan_catalog_detail', loan_id=loan.id)
    return render(request, 'loans/_return_status.html', {'loan': loan})
