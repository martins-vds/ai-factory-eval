from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone
from django.utils.html import format_html

from src.loans.repository import DjangoLoanRepository

from .services import calculate_late_fee

loan_repository = DjangoLoanRepository()


def fee_detail(request, loan_id):
    loan = loan_repository.find(loan_id)
    if loan is None:
        return HttpResponse('<p>No such loan.</p>', status=404, content_type='text/html')

    fee = calculate_late_fee(loan.due_on, loan.returned_on, timezone.localdate())
    return HttpResponse(
        format_html(
            '<h1>Late fee for {}</h1><p>Due {}, {} day(s) late.</p>'
            '<p class="fee">Fee: ${}</p>',
            loan.id,
            loan.due_on.isoformat(),
            fee.days_late,
            f'{fee.amount_cents // 100}.{fee.amount_cents % 100:02d}',
        ),
        content_type='text/html',
    )


def fee_page(request, loan_id):
    loan = loan_repository.find(loan_id)
    if loan is None:
        return HttpResponse('<p>No such loan.</p>', status=404, content_type='text/html')

    fee = calculate_late_fee(loan.due_on, loan.returned_on, timezone.localdate())
    return render(
        request,
        'fees/detail.html',
        {
            'loan': loan,
            'fee': fee,
            'amount': f'${fee.amount_cents // 100}.{fee.amount_cents % 100:02d}',
        },
    )
