from django.http import HttpResponse, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, redirect, render

from .composition import loan_application
from .forms import LoanForm
from .models import Loan
from .services import (
    LoanAlreadyReturned,
    LoanInputError,
    LoanNotFound,
    get_loan_text,
    list_loans_text,
)


def loan_catalog(request):
    return render(request, 'loans/list.html', {'loans': loan_application().all()})


def loan_catalog_new(request):
    if request.method == 'GET':
        return render(request, 'loans/new.html', {'form': LoanForm()})
    if request.method != 'POST':
        return HttpResponseNotAllowed(['GET', 'POST'])
    form = LoanForm(request.POST)
    if not form.is_valid():
        template = (
            'loans/partials/loan_errors.html'
            if request.headers.get('HX-Request') == 'true'
            else 'loans/new.html'
        )
        return render(request, template, {'form': form}, status=400)
    loan = loan_application().lend(form.cleaned_data['member'], form.cleaned_data['isbn'])
    if request.headers.get('HX-Request') == 'true':
        return render(
            request,
            'loans/partials/loan_feedback.html',
            {'loans': loan_application().all(), 'message': f'Loan {loan.id} recorded.'},
            status=201,
        )
    return redirect('/ui/loans/')


def loan_catalog_detail(request, loan_id):
    loan = get_object_or_404(Loan, pk=loan_id)
    return render(request, 'loans/detail.html', {'loan': loan})


def loan_list(request):
    if request.method == 'POST':
        if 'member' not in request.POST or 'isbn' not in request.POST:
            return HttpResponse(
                'member and isbn are required\n',
                status=400,
                content_type='text/plain',
            )
        application = loan_application()
        try:
            loan = application.lend(request.POST.get('member'), request.POST.get('isbn'))
        except LoanInputError as error:
            details = ''.join(f'{field}: {message}\n' for field, message in error.errors.items())
            return HttpResponse(details, status=400, content_type='text/plain')
        return HttpResponse(
            get_loan_text(loan),
            status=201,
            content_type='text/plain',
        )
    if request.method != 'GET':
        return HttpResponseNotAllowed(['GET', 'POST'])
    return HttpResponse(
        list_loans_text(loan_application().all()),
        content_type='text/plain',
    )


def loan_return(request, loan_id):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])
    try:
        loan = loan_application().return_loan(loan_id)
    except LoanNotFound:
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')
    except LoanAlreadyReturned:
        return HttpResponse('loan already returned\n', status=409, content_type='text/plain')
    return HttpResponse(get_loan_text(loan), content_type='text/plain')


def loan_catalog_return(request, loan_id):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])
    application = loan_application()
    try:
        loan = application.return_loan(loan_id)
    except LoanNotFound:
        return _loan_return_error(request, 'No such loan.', 404)
    except LoanAlreadyReturned:
        return _loan_return_error(request, 'This loan has already been returned.', 409)
    if request.headers.get('HX-Request') == 'true':
        return render(
            request,
            'loans/partials/loan_feedback.html',
            {'loans': application.all(), 'message': f'Loan {loan.id} returned.'},
        )
    return redirect('/ui/loans/')


def _loan_return_error(request, message, status):
    template = (
        'loans/partials/return_error.html'
        if request.headers.get('HX-Request') == 'true'
        else 'loans/return_error.html'
    )
    return render(request, template, {'message': message}, status=status)


def loan_detail(request, loan_id):
    body = get_loan_text(loan_application().find(loan_id))
    if body is None:
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')
    return HttpResponse(body, content_type='text/plain')
