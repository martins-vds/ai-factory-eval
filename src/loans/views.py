from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from .composition import lend_loan, return_loan
from .models import Loan
from .queries import get_loan_text, list_loans_text
from .services import InvalidLoan, LoanAlreadyReturned, LoanNotFound, loan_line


@require_http_methods(['GET', 'POST'])
def loan_catalog(request):
    if request.method == 'POST':
        return lend_loan_ui(request)
    return render(request, 'loans/list.html', {'loans': Loan.objects.all()})


@require_GET
def loan_catalog_new(request):
    return render(
        request,
        'loans/new.html',
        {'values': {'member': '', 'isbn': ''}, 'errors': {}},
    )


@require_GET
def loan_catalog_detail(request, loan_id):
    loan = get_object_or_404(Loan, pk=loan_id)
    return render(request, 'loans/detail.html', {'loan': loan})


@require_http_methods(['GET', 'POST'])
@csrf_exempt
def loan_list(request):
    if request.method == 'POST':
        try:
            loan = lend_loan(request.POST.get('member'), request.POST.get('isbn'))
        except InvalidLoan:
            return HttpResponse(
                'member and isbn are required\n',
                status=400,
                content_type='text/plain',
            )
        return HttpResponse(loan_line(loan), status=201, content_type='text/plain')
    return HttpResponse(list_loans_text(), content_type='text/plain')


@require_GET
def loan_detail(request, loan_id):
    body = get_loan_text(loan_id)
    if body is None:
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')
    return HttpResponse(body, content_type='text/plain')


@require_POST
@csrf_exempt
def loan_return_api(request, loan_id):
    try:
        loan = return_loan(loan_id)
    except LoanNotFound:
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')
    except LoanAlreadyReturned:
        return HttpResponse('loan already returned\n', status=409, content_type='text/plain')
    return HttpResponse(loan_line(loan), content_type='text/plain')


def lend_loan_ui(request):
    values = {
        'member': request.POST.get('member', ''),
        'isbn': request.POST.get('isbn', ''),
    }
    try:
        lend_loan(values['member'], values['isbn'])
    except InvalidLoan as error:
        context = {'values': values, 'errors': error.errors}
        template = (
            'loans/_lend_form.html'
            if request.headers.get('HX-Request') == 'true'
            else 'loans/new.html'
        )
        return render(request, template, context, status=400)
    if request.headers.get('HX-Request') == 'true':
        return HttpResponse(status=204, headers={'HX-Redirect': '/ui/loans/'})
    return HttpResponse(status=302, headers={'Location': '/ui/loans/'})


@require_POST
def loan_return_ui(request, loan_id):
    try:
        loan = return_loan(loan_id)
    except LoanNotFound:
        return render(
            request,
            'loans/_return_error.html',
            {'loan_id': loan_id, 'message': 'No such loan.'},
            status=404,
        )
    except LoanAlreadyReturned as error:
        return render(
            request,
            'loans/_loan_row.html',
            {
                'loan': error.loan,
                'error': 'This loan was already returned; the original date remains on record.',
            },
            status=409,
        )
    if request.headers.get('HX-Request') == 'true':
        return render(request, 'loans/_loan_row.html', {'loan': loan})
    return HttpResponse(status=302, headers={'Location': '/ui/loans/'})
