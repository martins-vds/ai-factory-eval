from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render

from .forms import LoanForm
from .models import Loan
from .services import get_loan_text, lend_loan, list_loans_text, loan_line


def loan_catalog(request):
    return render(request, 'loans/list.html', {'loans': Loan.objects.all()})


def loan_catalog_detail(request, loan_id):
    loan = get_object_or_404(Loan, pk=loan_id)
    return render(request, 'loans/detail.html', {'loan': loan})


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
