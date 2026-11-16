from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from .forms import LoanForm
from .models import Loan
from .repository import LoanAlreadyReturned
from .services import (
    get_loan_text,
    lend_loan,
    list_loans_text,
    loan_line,
    return_loan,
)


def loan_catalog(request):
    form = LoanForm()
    feedback = None
    feedback_role = 'status'
    if request.method == 'POST':
        form = LoanForm(request.POST)
        if form.is_valid():
            loan = lend_loan(form.cleaned_data['member'], form.cleaned_data['isbn'])
            form = LoanForm()
            feedback = f'Loan {loan.id} created.'

    return render(
        request,
        'loans/list.html',
        {
            'loans': Loan.objects.all(),
            'form': form,
            'feedback': feedback,
            'feedback_role': feedback_role,
        },
    )


@require_GET
def loan_new(request):
    return loan_catalog(request)


def loan_catalog_detail(request, loan_id):
    loan = get_object_or_404(Loan, pk=loan_id)
    return render(request, 'loans/detail.html', {'loan': loan})


# The public API has no session authentication and preserves the legacy form-post contract.
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
        loan = lend_loan(form.cleaned_data['member'], form.cleaned_data['isbn'])
        return HttpResponse(loan_line(loan), status=201, content_type='text/plain')

    return HttpResponse(list_loans_text(), content_type='text/plain')


def loan_detail(request, loan_id):
    body = get_loan_text(loan_id)
    if body is None:
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')
    return HttpResponse(body, content_type='text/plain')


@require_POST
@csrf_exempt
def loan_return(request, loan_id):
    try:
        loan = return_loan(loan_id)
    except LoanAlreadyReturned:
        return HttpResponse(
            'loan already returned\n',
            status=409,
            content_type='text/plain',
        )
    if loan is None:
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')
    return HttpResponse(loan_line(loan), content_type='text/plain')


@require_POST
def loan_return_ui(request, loan_id):
    try:
        loan = return_loan(loan_id)
    except LoanAlreadyReturned:
        return _render_loan_catalog(
            request,
            feedback='This loan was already returned; its original return date is unchanged.',
            feedback_role='alert',
        )
    if loan is None:
        return _render_loan_catalog(
            request,
            feedback='No such loan.',
            feedback_role='alert',
            status=404,
        )
    return _render_loan_catalog(
        request,
        feedback=f'Loan {loan.id} returned.',
    )


def _render_loan_catalog(request, feedback=None, feedback_role='status', status=200):
    return render(
        request,
        'loans/list.html',
        {
            'loans': Loan.objects.all(),
            'form': LoanForm(),
            'feedback': feedback,
            'feedback_role': feedback_role,
        },
        status=status,
    )
