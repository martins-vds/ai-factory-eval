from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.views.decorators.http import require_GET, require_POST

from src.loans.models import Loan

from .gateway import PaymentGatewayError, charge_loan
from .services import calculate_late_fee


def _fee_context(loan):
    fee = calculate_late_fee(loan)
    return {
        'loan': loan,
        'days_late': fee.days_late,
        'amount': f'{fee.amount_cents // 100}.{fee.amount_cents % 100:02d}',
        'fee_due': fee.amount_cents > 0,
    }


@require_GET
def fee_api(request, loan_id):
    loan = Loan.objects.filter(pk=loan_id).first()
    if loan is None:
        response = HttpResponse('<p>No such loan.</p>', status=404)
    else:
        body = render_to_string('fees/api.html', _fee_context(loan), request=request).rstrip('\n')
        response = HttpResponse(body)
    response['Content-Type'] = 'text/html'
    return response


@require_POST
def payment_api(request, loan_id):
    if not Loan.objects.filter(pk=loan_id).exists():
        return _plain_text('no such loan\n', status=404)
    try:
        gateway_status, body = charge_loan(loan_id)
    except PaymentGatewayError:
        return _plain_text('payment gateway unavailable\n', status=502)
    return _plain_text(body, status=200 if gateway_status == 200 else 502)


@require_GET
def fee_page(request, loan_id):
    loan = Loan.objects.filter(pk=loan_id).first()
    if loan is None:
        return HttpResponse('<p>No such loan.</p>', status=404)
    return render(request, 'fees/detail.html', _fee_context(loan))


@require_POST
def payment_page(request, loan_id):
    loan = Loan.objects.filter(pk=loan_id).first()
    if loan is None:
        return _plain_text('no such loan\n', status=404)
    try:
        gateway_status, body = charge_loan(loan_id)
    except PaymentGatewayError:
        return _plain_text('payment gateway unavailable\n', status=502)
    if gateway_status != 200:
        return _plain_text(body, status=502)
    if request.headers.get('HX-Request') != 'true':
        return redirect(f'/ui/fees/{loan_id}/')
    return render(request, 'fees/payment-status.html', {'loan': loan})


def _plain_text(body, status=200):
    response = HttpResponse(body, status=status)
    response['Content-Type'] = 'text/plain'
    return response
