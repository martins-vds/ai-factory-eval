from django.http import Http404, HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET, require_POST

from .composition import fee_application
from .services import PaymentGatewayFailure


@require_GET
def fee_api(_request, loan_id):
    fee = fee_application.calculate_fee(loan_id)
    if fee is None:
        return HttpResponse('<p>No such loan.</p>', status=404, content_type='text/html')

    body = (
        f'<h1>Late fee for {fee.loan.id}</h1>'
        f'<p>Due {fee.loan.due_on}, {fee.days_late} day(s) late.</p>'
        f'<p class="fee">Fee: {fee.amount}</p>'
    )
    return HttpResponse(body, content_type='text/html')


@require_GET
def fee_page(request, loan_id):
    fee = fee_application.calculate_fee(loan_id)
    if fee is None:
        raise Http404
    return render(request, 'fees/detail.html', {'fee': fee})


def _render_payment(request, loan_id, status, message, success):
    context = {'payment_message': message, 'payment_success': success}
    if request.headers.get('HX-Request') == 'true':
        return render(request, 'fees/payment-result.html', context, status=status)

    fee = fee_application.calculate_fee(loan_id)
    if fee is None:
        raise Http404
    return render(
        request,
        'fees/detail.html',
        {'fee': fee, **context},
        status=status,
    )


def _payment_response(request, loan_id, *, page):
    try:
        result = fee_application.pay(loan_id)
    except PaymentGatewayFailure as error:
        if page:
            return _render_payment(request, loan_id, 502, str(error), False)
        return HttpResponse(str(error), status=502, content_type='text/plain')

    if result is None:
        if page:
            return _render_payment(request, loan_id, 404, 'No such loan.', False)
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')

    status = 200 if result.status == 200 else 502
    if page:
        return _render_payment(request, loan_id, status, result.body, status == 200)
    return HttpResponse(result.body, status=status, content_type='text/plain')


@require_POST
def payment_api(request, loan_id):
    return _payment_response(request, loan_id, page=False)


@require_POST
def payment_page(request, loan_id):
    return _payment_response(request, loan_id, page=True)
