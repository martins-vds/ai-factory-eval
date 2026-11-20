from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import render
from django.views.decorators.http import require_GET

from .repositories import DjangoLoanRepository
from .services import export_loans, get_loan, list_loans


def _repository() -> DjangoLoanRepository:
    return DjangoLoanRepository()


@require_GET
def api_loan_list(request):
    return HttpResponse(export_loans(list_loans(_repository())), content_type='text/plain')


@require_GET
def api_loan_detail(request, loan_id: str):
    loan = get_loan(_repository(), loan_id)
    if loan is None:
        return HttpResponseNotFound('no such loan\n', content_type='text/plain')
    return HttpResponse(export_loans([loan]), content_type='text/plain')


@require_GET
def ui_loan_list(request):
    return render(request, 'loans/list.html', {'loans': list_loans(_repository())})


@require_GET
def ui_loan_detail(request, loan_id: str):
    loan = get_loan(_repository(), loan_id)
    if request.headers.get('HX-Request') == 'true':
        if loan is None:
            return render(request, 'loans/_not_found.html', status=404)
        return render(request, 'loans/_detail.html', {'loan': loan})
    return render(request, 'loans/detail.html', {'loan': loan}, status=200 if loan else 404)
