from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from .composition import loan_application
from .domain import LoanAlreadyReturned, LoanInputError, LoanNotFound
from .models import Loan
from .services import loan_line


def loan_catalog(request):
    return render(request, 'loans/list.html', {'loans': Loan.objects.all()})


def loan_catalog_detail(request, loan_id):
    loan = get_object_or_404(Loan, pk=loan_id)
    return render(request, 'loans/detail.html', {'loan': loan})


@require_GET
def loan_list(request):
    return HttpResponse(
        ''.join(loan_line(loan) for loan in loan_application().all_loans()),
        content_type='text/plain',
    )


@require_http_methods(['GET', 'POST'])
def loans(request):
    if request.method == 'POST':
        return loan_lend(request)
    return loan_list(request)


@require_GET
def loan_detail(request, loan_id):
    loan = loan_application().find_loan(loan_id)
    if loan is None:
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')
    return HttpResponse(loan_line(loan), content_type='text/plain')


@require_POST
def loan_lend(request):
    try:
        loan = loan_application().lend(
            request.POST.get('member'),
            request.POST.get('isbn'),
            timezone.localdate(),
        )
    except LoanInputError:
        return HttpResponse('member and isbn are required\n', status=400, content_type='text/plain')
    return HttpResponse(loan_line(loan), status=201, content_type='text/plain')


@require_POST
def loan_return(request, loan_id):
    try:
        loan = loan_application().return_loan(loan_id, timezone.localdate())
    except LoanNotFound:
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')
    except LoanAlreadyReturned:
        return HttpResponse('loan has already been returned\n', status=409, content_type='text/plain')
    return HttpResponse(loan_line(loan), content_type='text/plain')
