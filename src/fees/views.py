from django.http import HttpResponse
from django.utils import timezone
from django.utils.html import format_html
from django.views.decorators.http import require_GET

from src.loans.models import Loan

from .services import calculate_late_fee


@require_GET
def fee_api(request, loan_id):
    loan = Loan.objects.filter(pk=loan_id).first()
    if loan is None:
        return HttpResponse(
            '<p>No such loan.</p>',
            status=404,
            content_type='text/html',
        )

    days_late, amount_cents = calculate_late_fee(
        loan.due_on,
        loan.returned_on,
        timezone.localdate(),
    )
    amount = f'{amount_cents // 100}.{amount_cents % 100:02d}'
    body = format_html(
        '<h1>Late fee for {}</h1><p>Due {}, {} day(s) late.</p>'
        '<p class="fee">Fee: ${}</p>',
        loan.id,
        loan.due_on.isoformat(),
        days_late,
        amount,
    )
    return HttpResponse(body, content_type='text/html')
