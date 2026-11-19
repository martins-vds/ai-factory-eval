from datetime import date

from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from .composition import get_loan_service
from .forms import LoanForm
from .services import LoanAlreadyReturned, LoanInputError, loan_line


@require_http_methods(['GET', 'POST'])
def loan_lend_page(request):
    form = LoanForm(request.POST if request.method == 'POST' else None)
    if request.method == 'POST':
        if form.is_valid():
            try:
                get_loan_service().lend(
                    form.cleaned_data['member'],
                    form.cleaned_data['isbn'],
                    date.today(),
                )
            except LoanInputError as error:
                for field, message in error.field_errors.items():
                    form.add_error(field, message)
            else:
                if request.headers.get('HX-Request') == 'true':
                    return HttpResponse(status=204, headers={'HX-Redirect': '/ui/loans/'})
                return redirect('/ui/loans/')
        if request.headers.get('HX-Request') == 'true':
            response = render(request, 'loans/_lend_form.html', {'form': form})
        else:
            response = render(request, 'loans/new.html', {'form': form})
        response.status_code = 400
        return response
    return render(request, 'loans/new.html', {'form': form})


def loan_catalog(request):
    return render(request, 'loans/list.html', {'loans': get_loan_service().all()})


def loan_catalog_detail(request, loan_id):
    loan = get_loan_service().find(loan_id)
    if loan is None:
        return render(request, 'loans/not_found.html', status=404)
    return render(request, 'loans/detail.html', {'loan': loan})


@require_http_methods(['GET', 'POST'])
def loan_list(request):
    service = get_loan_service()
    if request.method == 'POST':
        try:
            loan = service.lend(
                request.POST.get('member'),
                request.POST.get('isbn'),
                date.today(),
            )
        except LoanInputError:
            return HttpResponse(
                'member and isbn are required\n',
                status=400,
                content_type='text/plain',
            )
        return HttpResponse(loan_line(loan), status=201, content_type='text/plain')
    return HttpResponse(service.list_text(), content_type='text/plain')


@require_POST
def loan_return(request, loan_id):
    try:
        loan = get_loan_service().mark_returned(loan_id, date.today())
    except LoanAlreadyReturned:
        return HttpResponse('already returned\n', status=409, content_type='text/plain')
    if loan is None:
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')
    return HttpResponse(loan_line(loan), content_type='text/plain')


@require_POST
def loan_return_page(request, loan_id):
    service = get_loan_service()
    is_htmx = request.headers.get('HX-Request') == 'true'
    try:
        loan = service.mark_returned(loan_id, date.today())
    except LoanAlreadyReturned:
        loan = service.find(loan_id)
        if is_htmx:
            return render(
                request,
                'loans/_loan_state.html',
                {'loan': loan, 'return_error': 'This loan has already been returned.'},
                status=409,
            )
        return render(
            request,
            'loans/detail.html',
            {'loan': loan, 'return_error': 'This loan has already been returned.'},
            status=409,
        )
    if loan is None:
        if is_htmx:
            return render(request, 'loans/_return_error.html', status=404)
        return render(request, 'loans/not_found.html', status=404)
    if is_htmx:
        return render(request, 'loans/_loan_state.html', {'loan': loan})
    return redirect('loan_catalog_detail', loan_id=loan_id)


@require_GET
def loan_detail(request, loan_id):
    body = get_loan_service().detail_text(loan_id)
    if body is None:
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')
    return HttpResponse(body, content_type='text/plain')
