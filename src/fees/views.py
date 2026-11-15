from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_GET, require_POST

from src.loans.repository import DjangoLoanRepository

from .services import calculate_late_fee, charge_late_fee


@require_GET
def fee_page(request, loan_id):
    loan = DjangoLoanRepository().find(loan_id)
    if loan is None:
        return HttpResponse('<p>No such loan.</p>', status=404, content_type='text/html')

    return render(
        request,
        'fees/detail.html',
        {'loan': loan, 'fee': calculate_late_fee(loan)},
    )


@require_GET
def fee_detail(request, loan_id):
    loan = DjangoLoanRepository().find(loan_id)
    if loan is None:
        return HttpResponse('<p>No such loan.</p>', status=404, content_type='text/html')

    fee = calculate_late_fee(loan)
    body = (
        f'<h1>Late fee for {loan.id}</h1>'
        f'<p>Due {loan.due_on.isoformat()}, {fee.days_late} day(s) late.</p>'
        f'<p class="fee">Fee: ${fee.amount:.2f}</p>'
    )
    return HttpResponse(body, content_type='text/html')


@require_POST
def payment_detail(request, loan_id):
    if DjangoLoanRepository().find(loan_id) is None:
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')

    result = charge_late_fee(loan_id)
    return HttpResponse(
        result.body,
        status=result.status_code,
        content_type='text/plain',
    )


@require_POST
def payment_page(request, loan_id):
    loan = DjangoLoanRepository().find(loan_id)
    if loan is None:
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')

    result = charge_late_fee(loan_id)
    body = result.body.decode('utf-8', errors='replace')
    if request.headers.get('HX-Request') == 'true':
        template = 'fees/payment-status.html'
        context = {'succeeded': result.status_code == 200, 'body': body}
    elif result.status_code == 200:
        return redirect('fee-page', loan_id=loan.id)
    else:
        template = 'fees/detail.html'
        context = {
            'loan': loan,
            'fee': calculate_late_fee(loan),
            'payment_error': body,
        }

    status = 200 if request.headers.get('HX-Request') == 'true' else result.status_code
    return render(request, template, context, status=status)
