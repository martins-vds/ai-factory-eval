def loan_line(loan):
    returned_on = loan.returned_on.isoformat() if loan.returned_on else ''
    return (
        f'{loan.id};{loan.member};{loan.isbn};{loan.lent_on.isoformat()};'
        f'{loan.due_on.isoformat()};{returned_on}\n'
    )
