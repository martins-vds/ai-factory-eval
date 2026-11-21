from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from .forms import LendLoanForm
from .models import Loan
from .repository import LoanRepository
from .services import (
    InvalidLoan,
    LoanAlreadyReturned,
    LoanNotFound,
    get_loan_text,
    lend_loan,
    list_loans_text,
    loan_line,
    return_loan,
)


def server_today():
    return timezone.localdate(timezone.now(), timezone.get_default_timezone())


@require_GET
def loan_catalog(request):
    return render(request, 'loans/list.html', {'loans': Loan.objects.all()})


@require_GET
def loan_catalog_detail(request, loan_id):
    loan = get_object_or_404(Loan, pk=loan_id)
    return render(request, 'loans/detail.html', {'loan': loan})


@require_http_methods(['GET', 'POST'])
def loan_lend_page(request):
    form = LendLoanForm(request.POST if request.method == 'POST' else None)
    if request.method == 'POST' and form.is_valid():
        try:
            loan = lend_loan(
                LoanRepository(),
                form.cleaned_data['member'],
                form.cleaned_data['isbn'],
                server_today(),
            )
        except InvalidLoan as error:
            for field, message in error.field_errors.items():
                form.add_error(field, message)
        else:
            if request.headers.get('HX-Request') == 'true':
                response = HttpResponse(status=204)
                response['HX-Redirect'] = f'/ui/loans/{loan.id}/'
                return response
            return redirect(f'/ui/loans/{loan.id}/')

    context = {'form': form}
    template = (
        'loans/_lend_form.html' if request.headers.get('HX-Request') == 'true' else 'loans/new.html'
    )
    status = 400 if request.method == 'POST' and form.errors else 200
    return render(request, template, context, status=status)


@require_POST
def loan_return_page(request, loan_id):
    is_htmx = request.headers.get('HX-Request') == 'true'
    try:
        loan = return_loan(LoanRepository(), loan_id, server_today())
    except LoanNotFound:
        if not is_htmx:
            return HttpResponse('no such loan\n', status=404, content_type='text/plain')
        return render(
            request,
            'loans/_return_action.html',
            {'error': 'no such loan'},
            status=404,
        )
    except LoanAlreadyReturned:
        loan = Loan.objects.get(pk=loan_id)
        if not is_htmx:
            return render(
                request,
                'loans/detail.html',
                {'loan': loan, 'return_error': True},
                status=409,
            )
        return render(
            request,
            'loans/_return_action.html',
            {'error': 'loan already returned', 'loan': loan},
            status=409,
        )
    if not is_htmx:
        return redirect(f'/ui/loans/{loan.id}/')
    return render(request, 'loans/_return_action.html', {'loan': loan})


@require_http_methods(['GET', 'POST'])
def loan_list(request):
    if request.method == 'POST':
        return loan_lend(request)
    return HttpResponse(list_loans_text(LoanRepository()), content_type='text/plain')


@require_GET
def loan_detail(request, loan_id):
    body = get_loan_text(LoanRepository(), loan_id)
    if body is None:
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')
    return HttpResponse(body, content_type='text/plain')


def loan_lend(request):
    try:
        loan = lend_loan(
            LoanRepository(),
            request.POST.get('member'),
            request.POST.get('isbn'),
            server_today(),
        )
    except InvalidLoan:
        return HttpResponse(
            'member and isbn are required\n',
            status=400,
            content_type='text/plain',
        )
    return HttpResponse(loan_line(loan), status=201, content_type='text/plain')


@require_POST
def loan_return(request, loan_id):
    try:
        loan = return_loan(LoanRepository(), loan_id, server_today())
    except LoanNotFound:
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')
    except LoanAlreadyReturned:
        return HttpResponse('loan already returned\n', status=409, content_type='text/plain')
    return HttpResponse(loan_line(loan), content_type='text/plain')
