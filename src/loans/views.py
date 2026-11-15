from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import LoanLendForm
from .models import Loan
from .services import get_loan_text, lend_loan, list_loans_text, loan_line, return_loan


def loan_catalog(request):
    return render(request, 'loans/list.html', {'loans': Loan.objects.all()})


def loan_catalog_detail(request, loan_id):
    loan = get_object_or_404(Loan, pk=loan_id)
    return render(request, 'loans/detail.html', {'loan': loan})


def loan_list(request):
    if request.method == 'POST':
        form = LoanLendForm(request.POST)
        if not form.is_valid():
            return HttpResponse(
                'member and isbn are required\n',
                status=400,
                content_type='text/plain',
            )
        loan = lend_loan(**form.cleaned_data)
        return HttpResponse(loan_line(loan), status=201, content_type='text/plain')
    if request.method != 'GET':
        return HttpResponse(status=405)
    return HttpResponse(list_loans_text(), content_type='text/plain')


def loan_lend(request):
    if request.method == 'GET':
        return render(request, 'loans/new.html')
    if request.method != 'POST':
        return HttpResponse(status=405)

    form = LoanLendForm(request.POST)
    if not form.is_valid():
        response = render(
            request,
            'loans/_loan_form.html'
            if request.headers.get('HX-Request') == 'true'
            else 'loans/new.html',
            {'form': form},
            status=400,
        )
        return response

    loan = lend_loan(**form.cleaned_data)
    if request.headers.get('HX-Request') == 'true':
        return render(
            request,
            'loans/_loan_form.html',
            {'message': f'Loan {loan.id} created.'},
            status=201,
        )
    return redirect('loan_catalog_detail', loan_id=loan.id)


def loan_detail(request, loan_id):
    body = get_loan_text(loan_id)
    if body is None:
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')
    return HttpResponse(body, content_type='text/plain')


def loan_return(request, loan_id):
    if request.method != 'POST':
        return HttpResponse(status=405)
    loan, first_return = return_loan(loan_id)
    if loan is None:
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')
    if not first_return:
        return HttpResponse('loan already returned\n', status=409, content_type='text/plain')
    return HttpResponse(loan_line(loan), content_type='text/plain')


def loan_return_ui(request, loan_id):
    if request.method != 'POST':
        return HttpResponse(status=405)
    loan, first_return = return_loan(loan_id)
    if loan is None:
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')
    if request.headers.get('HX-Request') == 'true':
        message = None if first_return else 'This loan has already been returned.'
        return render(
            request,
            'loans/_return_action.html',
            {'loan': loan, 'message': message},
        )
    if not first_return:
        return render(request, 'loans/detail.html', {'loan': loan}, status=409)
    return redirect('loan_catalog_detail', loan_id=loan.id)
