from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.http import require_GET

from src.loans.models import Loan

from .services import calculate_late_fee


def _fee_details(loan):
    fee = calculate_late_fee(
        due_on=loan.due_on,
        returned_on=loan.returned_on,
        today=timezone.localdate(),
    )
    amount = f'${fee.amount_cents // 100}.{fee.amount_cents % 100:02d}'
    return {'loan': loan, 'fee': fee, 'amount': amount}


def fee_api(request, loan_id):
    loan = Loan.objects.filter(pk=loan_id).first()
    if loan is None:
        return HttpResponse('<p>No such loan.</p>', status=404, content_type='text/html')

    details = _fee_details(loan)
    fee = details['fee']
    body = (
        f'<h1>Late fee for {loan.id}</h1>'
        f'<p>Due {loan.due_on.isoformat()}, {fee.days_late} day(s) late.</p>'
        f'<p class="fee">Fee: {details["amount"]}</p>'
    )
    return HttpResponse(body, content_type='text/html')


@require_GET
def fee_page(request, loan_id):
    loan = Loan.objects.filter(pk=loan_id).first()
    if loan is None:
        return HttpResponse('<p>No such loan.</p>', status=404, content_type='text/html')
    return render(request, 'fees/page.html', _fee_details(loan))
