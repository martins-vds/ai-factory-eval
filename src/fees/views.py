from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST

from src.loans.models import Loan

from .gateway import PaymentGatewayError, charge_loan
from .services import calculate_late_fee


@require_GET
def fee_api(request, loan_id):
    loan = Loan.objects.filter(pk=loan_id).first()
    if loan is None:
        return HttpResponse('<p>No such loan.</p>', status=404, content_type='text/html')

    fee = calculate_late_fee(loan.due_on, loan.returned_on, timezone.localdate())
    body = (
        f'<h1>Late fee for {loan.id}</h1>'
        f'<p>Due {loan.due_on.isoformat()}, {fee.days_late} day(s) late.</p>'
        f'<p class="fee">Fee: {fee.formatted_amount}</p>'
    )
    return HttpResponse(body, content_type='text/html')


@require_POST
def payment_api(request, loan_id):
    if not Loan.objects.filter(pk=loan_id).exists():
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')

    try:
        response = charge_loan(loan_id)
    except PaymentGatewayError:
        return HttpResponse(
            'payment gateway unavailable\n',
            status=502,
            content_type='text/plain',
        )
    return HttpResponse(response.body, status=response.status, content_type='text/plain')


@require_GET
def fee_page(request, loan_id):
    loan = get_object_or_404(Loan, pk=loan_id)
    today = timezone.localdate()
    fees = [
        {
            'loan': item,
            'fee': calculate_late_fee(item.due_on, item.returned_on, today),
        }
        for item in Loan.objects.all()
    ]
    fee = calculate_late_fee(loan.due_on, loan.returned_on, today)
    return render(request, 'fees/fee.html', {'loan': loan, 'fee': fee, 'fees': fees})


@require_POST
def payment_page(request, loan_id):
    if not Loan.objects.filter(pk=loan_id).exists():
        return render(
            request,
            'fees/payment-status.html',
            {'successful': False, 'body': 'No such loan.'},
        )

    try:
        response = charge_loan(loan_id)
    except PaymentGatewayError:
        successful = False
        body = 'payment gateway unavailable'
    else:
        successful = response.status == 200
        body = response.body.strip()

    return render(
        request,
        'fees/payment-status.html',
        {'successful': successful, 'body': body},
    )
