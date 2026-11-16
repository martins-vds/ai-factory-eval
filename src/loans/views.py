from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods, require_POST

from .forms import LoanLendingForm
from .models import Loan
from .services import get_loan_text, lend_loan, list_loans_text, loan_line, return_loan


def loan_catalog(request):
    return _render_loan_catalog(request)


def _render_loan_catalog(request, *, form=None, feedback=''):
    return render(
        request,
        'loans/list.html',
        {
            'loans': Loan.objects.all(),
            'form': form or LoanLendingForm(),
            'feedback': feedback,
        },
    )


@require_http_methods(['GET', 'POST'])
def loan_catalog_new(request):
    form = LoanLendingForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        loan = lend_loan(**form.cleaned_data)
        return _render_loan_catalog(request, feedback=f'Loan {loan.id} added to the collection.')
    return _render_loan_catalog(request, form=form)


@require_POST
def loan_catalog_return(request, loan_id):
    loan, marked_returned = return_loan(loan_id)
    if loan is None:
        feedback = 'No such loan.'
    elif marked_returned:
        feedback = f'{loan.id} marked returned today.'
    else:
        feedback = (
            f'{loan.id} was already returned on {loan.returned_on}; '
            'repeat return rejected and original date retained.'
        )
    return _render_loan_catalog(request, feedback=feedback)


def loan_catalog_detail(request, loan_id):
    loan = get_object_or_404(Loan, pk=loan_id)
    return render(request, 'loans/detail.html', {'loan': loan})


# Keep the characterized public API usable without browser CSRF tokens.
@csrf_exempt
@require_http_methods(['GET', 'POST'])
def loan_list(request):
    if request.method == 'POST':
        form = LoanLendingForm(request.POST)
        if not form.is_valid():
            return HttpResponse(
                'member and isbn are required\n', status=400, content_type='text/plain'
            )
        loan = lend_loan(**form.cleaned_data)
        return HttpResponse(loan_line(loan), status=201, content_type='text/plain')
    return HttpResponse(list_loans_text(), content_type='text/plain')


def loan_detail(request, loan_id):
    body = get_loan_text(loan_id)
    if body is None:
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')
    return HttpResponse(body, content_type='text/plain')


@csrf_exempt
@require_POST
def loan_return(request, loan_id):
    loan, marked_returned = return_loan(loan_id)
    if loan is None:
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')
    if not marked_returned:
        return HttpResponse('loan already returned\n', status=409, content_type='text/plain')
    return HttpResponse(loan_line(loan), content_type='text/plain')
