from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from .models import Loan
from .repository import LoanRepository
from .services import LoanValidationError, get_loan_text, lend_loan, list_loans_text


def loan_catalog(request):
    return render(request, 'loans/list.html', {'loans': Loan.objects.all()})


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
