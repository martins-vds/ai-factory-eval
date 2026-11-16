from urllib.parse import urlencode

from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .models import Loan
from .services import get_loan_text, lend_loan, list_loans_text, loan_line, return_loan


def loan_catalog(request):
    context = {}
    created = request.GET.get('created')
    returned = request.GET.get('returned')
    already_returned = request.GET.get('already_returned')
    if created:
        context['feedback'] = f'Loan {created} added to the collection.'
    elif returned:
        context['feedback'] = f'{returned} marked returned today.'
    elif already_returned:
        loan = Loan.objects.filter(pk=already_returned).first()
        if loan is not None:
            context['feedback'] = (
                f'{loan.id} was already returned on {loan.returned_on}; '
                'repeat return rejected and original date retained.'
            )
    return render(request, 'loans/list.html', _loan_catalog_context(**context))


def loan_catalog_detail(request, loan_id):
    loan = get_object_or_404(Loan, pk=loan_id)
    return render(request, 'loans/detail.html', {'loan': loan})


def loan_list(request):
    if request.method == 'POST':
        member = request.POST.get('member', '')
        isbn = request.POST.get('isbn', '')
        if not member.strip() or not isbn.strip():
            return HttpResponse(
                'member and isbn are required\n',
                status=400,
                content_type='text/plain',
            )
        return HttpResponse(
            loan_line(lend_loan(member, isbn)),
            status=201,
            content_type='text/plain',
        )
    return HttpResponse(list_loans_text(), content_type='text/plain')


def loan_detail(request, loan_id):
    body = get_loan_text(loan_id)
    if body is None:
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')
    return HttpResponse(body, content_type='text/plain')


@require_POST
def loan_return(request, loan_id):
    loan, updated = return_loan(loan_id)
    if loan is None:
        return HttpResponse('no such loan\n', status=404, content_type='text/plain')
    if not updated:
        return HttpResponse('loan already returned\n', status=409, content_type='text/plain')
    return HttpResponse(loan_line(loan), content_type='text/plain')


@require_POST
def loan_lend_ui(request):
    form_values = {
        'member': request.POST.get('member', ''),
        'isbn': request.POST.get('isbn', ''),
    }
    errors = {}
    if not form_values['member'].strip():
        errors['member'] = 'Enter a member name; blank values are not accepted.'
    if not form_values['isbn'].strip():
        errors['isbn'] = 'Enter an ISBN; blank values are not accepted.'
    if errors:
        return render(
            request,
            'loans/list.html',
            _loan_catalog_context(form_values=form_values, errors=errors),
        )

    loan = lend_loan(form_values['member'].strip(), form_values['isbn'].strip())
    if request.headers.get('HX-Request') == 'true':
        return render(
            request,
            'loans/list.html',
            _loan_catalog_context(feedback=f'Loan {loan.id} added to the collection.'),
        )
    return redirect(f'/ui/loans/?{urlencode({"created": loan.id})}')


@require_POST
def loan_return_ui(request, loan_id):
    loan, updated = return_loan(loan_id)
    if loan is None:
        return HttpResponse('No such loan.', status=404)

    if updated:
        feedback = f'{loan.id} marked returned today.'
        query = urlencode({'returned': loan.id})
    else:
        feedback = (
            f'{loan.id} was already returned on {loan.returned_on}; '
            'repeat return rejected and original date retained.'
        )
        query = urlencode({'already_returned': loan.id})

    if request.headers.get('HX-Request') == 'true':
        return render(
            request,
            'loans/list.html',
            _loan_catalog_context(feedback=feedback),
        )
    return redirect(f'/ui/loans/?{query}')


def _loan_catalog_context(**overrides):
    context = {'loans': Loan.objects.all()}
    context.update(overrides)
    return context
