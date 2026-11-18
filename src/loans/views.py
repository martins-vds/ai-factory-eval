from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods, require_POST

from .models import Loan
from .repository import LoanRepository
from .services import (
    LoanAlreadyReturnedError,
    LoanNotFoundError,
    LoanValidationError,
    get_loan_text,
    lend_loan,
    list_loans_text,
    loan_line,
    return_loan,
)


def loan_catalog(request):
    return render(request, 'loans/list.html', {'loans': Loan.objects.all()})


def loan_catalog_records(request):
    return render(request, 'loans/_records.html', {'loans': Loan.objects.all()})


def loan_catalog_detail(request, loan_id):
    loan = get_object_or_404(Loan, pk=loan_id)
    return render(request, 'loans/detail.html', {'loan': loan})


@require_http_methods(['GET', 'POST'])
def loan_list(request):
    if request.method == 'POST':
        return loan_lend(request)
    return HttpResponse(list_loans_text(LoanRepository()), content_type='text/plain')


def loan_detail(request, loan_id):
    body = get_loan_text(loan_id, LoanRepository())
    if body is None:
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')
    return HttpResponse(body, content_type='text/plain')


def loan_lend(request):
    store = LoanRepository()
    try:
        loan = lend_loan(
            request.POST.get('member'),
            request.POST.get('isbn'),
            timezone.localdate(),
            store,
        )
    except LoanValidationError:
        return HttpResponse(
            'member and isbn are required\n',
            status=400,
            content_type='text/plain',
        )
    return HttpResponse(
        get_loan_text(loan.id, store),
        status=201,
        content_type='text/plain',
    )


@require_POST
def loan_return(request, loan_id):
    try:
        loan = return_loan(loan_id, timezone.localdate(), LoanRepository())
    except LoanNotFoundError:
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')
    except LoanAlreadyReturnedError:
        return HttpResponse('loan already returned\n', status=409, content_type='text/plain')
    return HttpResponse(loan_line(loan), content_type='text/plain')


@require_POST
def loan_catalog_lend(request):
    try:
        loan = lend_loan(
            request.POST.get('member'),
            request.POST.get('isbn'),
            timezone.localdate(),
            LoanRepository(),
        )
    except LoanValidationError as error:
        context = {
            'loans': Loan.objects.all(),
            'errors': error.errors,
            'member': request.POST.get('member', ''),
            'isbn': request.POST.get('isbn', ''),
        }
        if request.headers.get('HX-Request') == 'true':
            return render(request, 'loans/_lend_result.html', context, status=400)
        return render(request, 'loans/list.html', context, status=400)

    if request.headers.get('HX-Request') == 'true':
        response = render(request, 'loans/_lend_result.html', {'loan': loan}, status=201)
        response['HX-Trigger'] = 'loan-updated'
        return response
    return render(
        request,
        'loans/list.html',
        {'loans': Loan.objects.all(), 'created': loan},
        status=201,
    )


@require_POST
def loan_catalog_return(request, loan_id):
    store = LoanRepository()
    try:
        loan = return_loan(loan_id, timezone.localdate(), store)
    except LoanNotFoundError:
        if request.headers.get('HX-Request') == 'true':
            return render(
                request,
                'loans/_return_control.html',
                {'error': 'No such loan.'},
                status=404,
            )
        return render(request, 'loans/not_found.html', status=404)
    except LoanAlreadyReturnedError:
        loan = store.find(loan_id)
        if request.headers.get('HX-Request') == 'true':
            return render(
                request,
                'loans/_return_control.html',
                {'loan': loan, 'error': 'This loan has already been returned.'},
                status=409,
            )
        return render(
            request,
            'loans/detail.html',
            {'loan': loan, 'message': 'This loan has already been returned.'},
            status=409,
        )

    if request.headers.get('HX-Request') == 'true':
        response = render(request, 'loans/_return_control.html', {'loan': loan})
        response['HX-Trigger'] = 'loan-updated'
        return response
    return redirect('loan-catalog-detail', loan_id=loan.id)
