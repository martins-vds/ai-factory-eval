from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_GET, require_POST

from .composition import fee_application, payment_application
from .services import PaymentGatewayError, PaymentResult


def _fee_not_found(request, *, browser):
    if browser:
        return render(request, 'fees/not-found.html', status=404)
    return HttpResponse('<p>No such loan.</p>', status=404, content_type='text/html')


def _fee_context(fee):
    amount = f'${fee.amount_cents // 100}.{fee.amount_cents % 100:02d}'
    return {
        'fee': fee,
        'amount': amount,
    }


def _payment_result(request, loan_id, *, browser):
    try:
        result = payment_application.pay(loan_id)
    except PaymentGatewayError as error:
        result = PaymentResult(502, f'{error}\n')

    if result is None:
        if browser and request.headers.get('HX-Request') == 'true':
            return render(request, 'fees/payment-result.html', {'missing': True}, status=404)
        if browser:
            return _fee_not_found(request, browser=True)
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')

    if browser:
        context = {
            'body': result.body,
            'success': result.status_code == 200,
        }
        if request.headers.get('HX-Request') == 'true':
            return render(
                request,
                'fees/payment-result.html',
                context,
                status=result.status_code,
            )
        if result.status_code == 200:
            return redirect(f'/ui/fees/{loan_id}/')

        fee = fee_application.calculate(loan_id)
        if fee is None:
            return _fee_not_found(request, browser=True)
        return render(
            request,
            'fees/page.html',
            {**_fee_context(fee), 'payment_result': context},
            status=result.status_code,
        )

    return HttpResponse(result.body, status=result.status_code, content_type='text/plain')


@require_GET
def fee_detail(request, loan_id):
    fee = fee_application.calculate(loan_id)
    if fee is None:
        return _fee_not_found(request, browser=False)

    context = _fee_context(fee)
    amount = context['amount']
    body = (
        f'<h1>Late fee for {fee.loan_id}</h1>'
        f'<p>Due {fee.due_on.isoformat()}, {fee.late_days} day(s) late.</p>'
        f'<p class="fee">Fee: {amount}</p>'
    )
    return HttpResponse(body, content_type='text/html')


@require_GET
def fee_page(request, loan_id):
    fee = fee_application.calculate(loan_id)
    if fee is None:
        return _fee_not_found(request, browser=True)
    return render(request, 'fees/page.html', _fee_context(fee))


@require_POST
def payment(request, loan_id):
    return _payment_result(request, loan_id, browser=False)


@require_POST
def payment_page(request, loan_id):
    return _payment_result(request, loan_id, browser=True)
