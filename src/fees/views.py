from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST

from src.loans.models import Loan

from .calculation import calculate_late_fee
from .gateway import charge_loan


def fee_quote(loan):
    return calculate_late_fee(loan.due_on, loan.returned_on, timezone.localdate())


@require_GET
def fee_api(request, loan_id):
    loan = Loan.objects.filter(pk=loan_id).first()
    if loan is None:
        return HttpResponse('<p>No such loan.</p>', status=404, content_type='text/html')

    quote = fee_quote(loan)
    body = (
        f'<h1>Late fee for {loan.id}</h1><p>Due {loan.due_on.isoformat()}, '
        f'{quote.late_days} day(s) late.</p><p class="fee">Fee: ${quote.amount:.2f}</p>'
    )
    return HttpResponse(body, content_type='text/html')


@require_GET
def fee_page(request, loan_id):
    loan = get_object_or_404(Loan, pk=loan_id)
    return render(request, 'fees/detail.html', {'loan': loan, 'quote': fee_quote(loan)})


def payment_result(loan_id):
    if not Loan.objects.filter(pk=loan_id).exists():
        return None

    result = charge_loan(loan_id)
    status = 200 if result.status == 200 else 502
    return result, status


@require_POST
def payment_api(request, loan_id):
    outcome = payment_result(loan_id)
    if outcome is None:
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')

    result, status = outcome
    return HttpResponse(result.body, status=status, content_type='text/plain')


@require_POST
def payment_page(request, loan_id):
    outcome = payment_result(loan_id)
    if outcome is None:
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')

    _, status = outcome
    if request.headers.get('HX-Request') == 'true':
        return render(
            request,
            'fees/payment-status.html',
            {'succeeded': status == 200},
        )
    if status == 200:
        return redirect('ui-fee-page', loan_id=loan_id)
    loan = get_object_or_404(Loan, pk=loan_id)
    return render(
        request,
        'fees/detail.html',
        {'loan': loan, 'quote': fee_quote(loan), 'payment_error': True},
        status=status,
    )
