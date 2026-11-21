import csv
from io import StringIO


class RequiredLoanFieldError(ValueError):
    pass


class LoanNotFoundError(LookupError):
    pass


class LoanAlreadyReturnedError(RuntimeError):
    pass


def lend_loan(member, isbn, repository, today):
    if not member or not member.strip() or not isbn or not isbn.strip():
        raise RequiredLoanFieldError
    loan = repository.create(
        id=repository.next_id(),
        member=member,
        isbn=isbn,
        lent_on=today,
    )
    return loan


def return_loan(loan_id, repository, today):
    loan = repository.find(loan_id)
    if loan is None:
        raise LoanNotFoundError
    if loan.returned_on is not None:
        raise LoanAlreadyReturnedError
    repository.mark_returned(loan, today)
    return loan


def loan_line(loan):
    output = StringIO(newline='')
    writer = csv.writer(output, delimiter=';', lineterminator='\n')
    writer.writerow(
        [
            loan.id,
            loan.member,
            loan.isbn,
            loan.lent_on.isoformat(),
            loan.due_on.isoformat(),
            loan.returned_on.isoformat() if loan.returned_on else '',
        ]
    )
    return output.getvalue()


def list_loans_text(repository):
    return ''.join(loan_line(loan) for loan in repository.all())


def get_loan_text(loan_id, repository):
    loan = repository.find(loan_id)
    return loan_line(loan) if loan else None
