from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods, require_POST

from .forms import LoanForm
from .models import Loan
from .repository import LoanRepository
from .services import (
    LoanAlreadyReturned,
    LoanInputError,
    LoanNotFound,
    get_loan_text,
    lend_loan,
    list_loans_text,
    loan_line,
    return_loan,
)


def _is_htmx(request):
    return request.headers.get('HX-Request', '').lower() == 'true'


def loan_catalog(request):
    return render(request, 'loans/list.html', {'loans': Loan.objects.all()})


def loan_catalog_detail(request, loan_id):
    loan = Loan.objects.filter(pk=loan_id).first()
    if loan is None:
        return render(request, 'loans/not_found.html', status=404)
    return render(request, 'loans/detail.html', {'loan': loan})


@require_http_methods(['GET', 'POST'])
def loan_list(request):
    if request.method == 'POST':
        return loan_lend(request)
    return HttpResponse(
        list_loans_text(LoanRepository()),
        content_type='text/plain',
    )


def loan_detail(request, loan_id):
    body = get_loan_text(loan_id, LoanRepository())
    if body is None:
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')
    return HttpResponse(body, content_type='text/plain')


@require_POST
def loan_lend(request):
    try:
        loan = lend_loan(
            request.POST.get('member'),
            request.POST.get('isbn'),
            LoanRepository(),
            timezone.localdate(),
        )
    except LoanInputError:
        return HttpResponse(
            'member and isbn are required\n',
            status=400,
            content_type='text/plain',
        )
    return HttpResponse(
        loan_line(loan),
        status=201,
        content_type='text/plain',
    )


@require_POST
def loan_return(request, loan_id):
    try:
        loan = return_loan(loan_id, LoanRepository(), timezone.localdate())
    except LoanNotFound:
        return HttpResponse(
            'no such loan\n',
            status=404,
            content_type='text/plain',
        )
    except LoanAlreadyReturned:
        return HttpResponse(
            'loan already returned\n',
            status=409,
            content_type='text/plain',
        )
    return HttpResponse(loan_line(loan), content_type='text/plain')


@require_http_methods(['GET', 'POST'])
def loan_lend_page(request):
    form = LoanForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        try:
            loan = lend_loan(
                form.cleaned_data['member'],
                form.cleaned_data['isbn'],
                LoanRepository(),
                timezone.localdate(),
            )
        except LoanInputError as error:
            for field, message in error.errors.items():
                form.add_error(field, message)
        else:
            if _is_htmx(request):
                return render(request, 'loans/_lend_success.html', {'loan': loan})
            return redirect('loan-detail-ui', loan_id=loan.id)

    template = 'loans/_lend_form.html' if _is_htmx(request) else 'loans/new.html'
    return render(request, template, {'form': form})


@require_POST
def loan_return_page(request, loan_id):
    repository = LoanRepository()
    try:
        loan = return_loan(loan_id, repository, timezone.localdate())
    except LoanNotFound:
        if _is_htmx(request):
            return render(
                request,
                'loans/_return_status.html',
                {'error': 'No such loan.'},
            )
        return render(request, 'loans/not_found.html', status=404)
    except LoanAlreadyReturned:
        loan = repository.find(loan_id)
        if _is_htmx(request):
            return render(
                request,
                'loans/_return_status.html',
                {'loan': loan, 'error': 'This loan has already been returned.'},
            )
        return render(
            request,
            'loans/detail.html',
            {'loan': loan, 'error': 'This loan has already been returned.'},
            status=409,
        )

    if _is_htmx(request):
        return render(request, 'loans/_return_status.html', {'loan': loan})
    return redirect('loan-detail-ui', loan_id=loan.id)
