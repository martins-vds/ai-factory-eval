from django.http import HttpResponse
from django.shortcuts import render
from django.utils.html import escape
from django.views.decorators.http import require_POST

from .composition import fee_application, payment_application


def fee_api(request, loan_id):
    quote = fee_application.calculate_fee(loan_id)
    if quote is None:
        return HttpResponse('<p>No such loan.</p>', status=404, content_type='text/html')

    amount = format_fee_amount(quote.amount_cents)
    body = (
        f'<h1>Late fee for {escape(quote.loan.id)}</h1>'
        f'<p>Due {quote.loan.due_on.isoformat()}, {quote.late_days} day(s) late.</p>'
        f'<p class="fee">Fee: ${amount}</p>'
    )
    return HttpResponse(body, content_type='text/html')


def fee_page(request, loan_id):
    quote = fee_application.calculate_fee(loan_id)
    if quote is None:
        return render(request, 'fees/not-found.html', status=404)
    context = fee_page_context(quote)
    return render(request, 'fees/page.html', context)


@require_POST
def payment_api(request, loan_id):
    result = payment_application.pay(loan_id)
    if result is None:
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')
    return HttpResponse(result.body, status=result.status_code, content_type='text/plain')


@require_POST
def payment_page(request, loan_id):
    result = payment_application.pay(loan_id)
    if result is None:
        context = {'success': False, 'message': 'No such loan.'}
        return render(request, 'fees/payment-status.html', context, status=404)

    context = {
        'success': result.status_code == 200,
        'message': 'Payment received.' if result.status_code == 200 else result.body,
    }
    if request.headers.get('HX-Request') == 'true':
        return render(
            request,
            'fees/payment-status.html',
            context,
            status=result.status_code,
        )

    quote = fee_application.calculate_fee(loan_id)
    if quote is None:
        return render(request, 'fees/not-found.html', status=404)
    return render(
        request,
        'fees/page.html',
        fee_page_context(quote, context),
        status=result.status_code,
    )


def fee_page_context(quote, payment_status=None):
    return {
        'quote': quote,
        'fee_amount': format_fee_amount(quote.amount_cents),
        'payment_status': payment_status,
    }


def format_fee_amount(amount_cents):
    return f'{amount_cents // 100}.{amount_cents % 100:02d}'
