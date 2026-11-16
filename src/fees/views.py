from django.http import HttpResponse
from django.template.loader import render_to_string
from django.views.decorators.http import require_GET

from src.loans.models import Loan

from .services import calculate_late_fee


def _fee_context(loan):
    fee = calculate_late_fee(loan)
    return {
        'loan': loan,
        'days_late': fee.days_late,
        'amount': f'{fee.amount_cents // 100}.{fee.amount_cents % 100:02d}',
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
