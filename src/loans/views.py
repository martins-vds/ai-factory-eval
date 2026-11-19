from django.http import HttpResponse, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, render
from django.utils import timezone

from .models import Loan
from .repository import LoanRepository
from .services import (
    LoanInputError,
    get_loan_text,
    lend_loan,
    list_loans_text,
    loan_line,
)


def loan_catalog(request):
    return render(request, 'loans/list.html', {'loans': Loan.objects.all()})


def loan_catalog_detail(request, loan_id):
    loan = get_object_or_404(Loan, pk=loan_id)
    return render(request, 'loans/detail.html', {'loan': loan})


def loan_list(request):
    if request.method == 'POST':
        try:
            loan = lend_loan(
                repository=LoanRepository(),
                member=request.POST.get('member'),
                isbn=request.POST.get('isbn'),
                lent_on=timezone.localdate(),
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
    if request.method != 'GET':
        return HttpResponseNotAllowed(['GET', 'POST'])
    return HttpResponse(
        list_loans_text(LoanRepository()),
        content_type='text/plain',
    )


def loan_detail(request, loan_id):
    body = get_loan_text(loan_id, LoanRepository())
    if body is None:
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')
    return HttpResponse(body, content_type='text/plain')
