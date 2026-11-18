from django.http import HttpResponse
from django.shortcuts import render
from django.utils.html import format_html
from django.views.decorators.http import require_GET, require_POST

from .composition import fee_application, payment_application


@require_GET
def fee_api(request, loan_id):
    fee = fee_application.calculate(loan_id)
    if fee is None:
        return HttpResponse('<p>No such loan.</p>', status=404, content_type='text/html')

    body = format_html(
        '<h1>Late fee for {}</h1><p>Due {}, {} day(s) late.</p><p class="fee">Fee: {}</p>',
        fee.loan.id,
        fee.loan.due_on,
        fee.late_days,
        fee.amount,
    )
    return HttpResponse(body, content_type='text/html')


@require_GET
def fee_page(request, loan_id):
    fees = fee_application.all_fees()
    fee = next((item for item in fees if item.loan.id == loan_id), None)
    if fee is None:
        return render(request, 'fees/not-found.html', status=404)

    return render(
        request,
        'fees/detail.html',
        {'fee': fee, 'fees': fees},
    )


@require_POST
def payment_api(request, loan_id):
    result = payment_application.pay(loan_id)
    return HttpResponse(result.body, status=result.status_code, content_type='text/plain')


@require_POST
def payment_page(request, loan_id):
    result = payment_application.pay(loan_id)
    context = {'result': result}

    if request.headers.get('HX-Request') == 'true':
        return render(
            request,
            'fees/payment-status.html',
            context,
            status=result.status_code,
        )

    if result.loan is None:
        return render(request, 'fees/not-found.html', context, status=404)

    fee = fee_application.calculate_for(result.loan)
    context.update(
        {
            'fee': fee,
            'fees': fee_application.all_fees(),
        }
    )
    return render(
        request,
        'fees/detail.html',
        context,
        status=result.status_code,
    )
