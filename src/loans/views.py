from django.http import Http404, HttpResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from .composition import loan_application
from .domain import LoanAlreadyReturned, LoanInputError, LoanNotFound
from .services import get_loan_text, list_loans_text, loan_line


def loan_catalog(request):
    return render(request, 'loans/list.html', {'loans': loan_application().all_loans()})


def loan_catalog_detail(request, loan_id):
    loan = loan_application().find_loan(loan_id)
    if loan is None:
        raise Http404
    return render(request, 'loans/detail.html', {'loan': loan})


@require_GET
def loan_list(request):
    return HttpResponse(list_loans_text(loan_application()), content_type='text/plain')


@require_http_methods(['GET', 'POST'])
def loans(request):
    if request.method == 'POST':
        return loan_lend(request)
    return loan_list(request)


@require_GET
def loan_detail(request, loan_id):
    body = get_loan_text(loan_id, loan_application())
    if body is None:
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')
    return HttpResponse(body, content_type='text/plain')


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
        return HttpResponse(
            'loan has already been returned\n', status=409, content_type='text/plain'
        )
    return HttpResponse(loan_line(loan), content_type='text/plain')


@require_POST
def loan_lend_from_page(request):
    values = {'member': request.POST.get('member', ''), 'isbn': request.POST.get('isbn', '')}
    application = loan_application()
    try:
        loan = application.lend(values['member'], values['isbn'], timezone.localdate())
    except LoanInputError as error:
        context = {'errors': error.fields, 'values': values}
        if request.headers.get('HX-Request') == 'true':
            return render(request, 'loans/_lend_form.html', context, status=400)
        return render(request, 'loans/new.html', context, status=400)

    if request.headers.get('HX-Request') == 'true':
        return render(request, 'loans/_lend_result.html', {'loan': loan}, status=201)
    return redirect('loan-catalog-detail', loan_id=loan.id)


@require_http_methods(['GET', 'POST'])
def loan_lend_page(request):
    if request.method == 'POST':
        return loan_lend_from_page(request)
    return render(request, 'loans/new.html')


@require_POST
def loan_return_from_page(request, loan_id):
    application = loan_application()
    try:
        loan = application.return_loan(loan_id, timezone.localdate())
    except LoanNotFound:
        if request.headers.get('HX-Request') == 'true':
            return render(request, 'loans/_ui_error.html', status=404)
        return render(request, 'loans/ui_error.html', status=404)
    except LoanAlreadyReturned:
        loan = application.find_loan(loan_id)
        context = {'loan': loan, 'error': 'This loan has already been returned.'}
        if request.headers.get('HX-Request') == 'true':
            return render(request, 'loans/_return_form.html', context, status=409)
        return render(request, 'loans/detail.html', context, status=409)

    if request.headers.get('HX-Request') == 'true':
        return render(request, 'loans/_return_form.html', {'loan': loan})
    return redirect('loan-catalog-detail', loan_id=loan.id)
