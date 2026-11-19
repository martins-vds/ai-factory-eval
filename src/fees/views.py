from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET, require_POST

from .composition import fee_application, payment_application


def _fee_amount(fee):
    return f'{fee.fee_cents // 100}.{fee.fee_cents % 100:02d}'


def _api_response(body, status, content_type):
    response = HttpResponse(body, status=status, content_type=content_type)
    response['Content-Type'] = content_type
    return response


@require_GET
def fee_api(request, loan_id):
    fee = fee_application.calculate(loan_id)
    if fee is None:
        return _api_response('<p>No such loan.</p>', 404, 'text/html')

    body = (
        f'<h1>Late fee for {fee.loan_id}</h1>'
        f'<p>Due {fee.due_on.isoformat()}, {fee.late_days} day(s) late.</p>'
        f'<p class="fee">Fee: ${_fee_amount(fee)}</p>'
    )
    return _api_response(body, 200, 'text/html')


@require_GET
def fee_page(request, loan_id):
    fee = fee_application.calculate(loan_id)
    context = {
        'fee': fee,
        'fee_amount': _fee_amount(fee) if fee else None,
    }
    return render(request, 'fees/page.html', context, status=200 if fee else 404)


@require_POST
def payment_api(request, loan_id):
    result = payment_application.pay(loan_id)
    if result is None:
        return _api_response('no such loan\n', 404, 'text/plain')
    return _api_response(result.body, result.status_code, 'text/plain')


@require_POST
def payment_page(request, loan_id):
    result = payment_application.pay(loan_id)
    if result is None:
        status = 404
        success = False
        message = 'No such loan.'
    else:
        status = result.status_code
        success = status == 200
        message = result.body.strip()

    context = {'success': success, 'message': message}
    template = (
        'fees/payment-status.html'
        if request.headers.get('HX-Request') == 'true'
        else 'fees/payment-result.html'
    )
    return render(request, template, context, status=status)
