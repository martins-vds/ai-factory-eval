import csv
import io

from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import render

from src.loans.repository import LoanRepository


def _loan_line(loan):
    output = io.StringIO(newline='')
    csv.writer(output, delimiter=';', lineterminator='\n').writerow(
        [
            loan.pk,
            loan.member,
            loan.isbn,
            loan.lent_on.isoformat(),
            loan.due_on.isoformat(),
            loan.returned_on.isoformat() if loan.returned_on else '',
        ]
    )
    return output.getvalue()


def loan_list(request):
    loans = LoanRepository().all()
    output = io.StringIO(newline='')
    writer = csv.writer(output, delimiter=';', lineterminator='\n')
    writer.writerows(
        [
            [
                loan.pk,
                loan.member,
                loan.isbn,
                loan.lent_on.isoformat(),
                loan.due_on.isoformat(),
                loan.returned_on.isoformat() if loan.returned_on else '',
            ]
            for loan in loans
        ]
    )
    return HttpResponse(output.getvalue(), content_type='text/plain')


def loan_detail(request, loan_id):
    loan = LoanRepository().get(loan_id)
    if loan is None:
        return HttpResponseNotFound('no such loan\n', content_type='text/plain')
    return HttpResponse(_loan_line(loan), content_type='text/plain')


def loan_catalog(request):
    return render(request, 'loans/catalog.html', {'loans': LoanRepository().all()})


def loan_page(request, loan_id):
    loan = LoanRepository().get(loan_id)
    if loan is None:
        return render(request, 'loans/not_found.html', status=404)
    return render(request, 'loans/detail.html', {'loan': loan})
