from django.http import HttpResponse
from django.shortcuts import render
from django.utils.html import format_html
from django.views.decorators.http import require_POST

from .composition import fee_application, payment_application


def fee_api(request, loan_id):
    quote = fee_application.calculate(loan_id)
    if quote is None:
        response = HttpResponse('<p>No such loan.</p>', status=404, content_type='text/html')
    else:
        amount = f'{quote.amount_cents // 100}.{quote.amount_cents % 100:02d}'
        body = format_html(
            '<h1>Late fee for {}</h1><p>Due {}, {} day(s) late.</p><p class="fee">Fee: ${}</p>',
            quote.loan.id,
            quote.loan.due_on.isoformat(),
            quote.days_late,
            amount,
        )
        response = HttpResponse(body, content_type='text/html')
    response['Content-Type'] = 'text/html'
    return response


@require_POST
def payment_api(request, loan_id):
    result = payment_application.pay(loan_id)
    if result is None:
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')
    return HttpResponse(result.body, status=result.status_code, content_type='text/plain')


def fee_page(request, loan_id):
    quote = fee_application.calculate(loan_id)
    if quote is None:
        return render(
            request,
            'fees/not-found.html',
            status=404,
        )
    amount = f'{quote.amount_cents // 100}.{quote.amount_cents % 100:02d}'
    return render(request, 'fees/fee-page.html', {'quote': quote, 'amount': amount})


@require_POST
def payment_page(request, loan_id):
    result = payment_application.pay(loan_id)
    status_code = result.status_code if result is not None else 404
    context = {
        'loan_id': loan_id,
        'result': result,
        'status_code': status_code,
    }
    if request.headers.get('HX-Request') == 'true':
        return render(request, 'fees/payment-result.html', context, status=status_code)
    return render(
        request,
        'fees/payment-result-page.html',
        context,
        status=status_code,
    )
