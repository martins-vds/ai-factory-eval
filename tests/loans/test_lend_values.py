from datetime import timedelta

import pytest
from django.utils import timezone

from src.loans.models import Loan


@pytest.mark.django_db
def test_lend_endpoint_preserves_padded_member_and_isbn(client):
    lent_on = timezone.localdate()
    due_on = lent_on + timedelta(days=14)

    response = client.post('/loans', {'member': ' m1 ', 'isbn': ' 978-0 '})

    assert response.status_code == 201
    assert response.content.decode() == (
        f'L4; m1 ; 978-0 ;{lent_on.isoformat()};{due_on.isoformat()};\n'
    )
    loan = Loan.objects.get(pk='L4')
    assert loan.member == ' m1 '
    assert loan.isbn == ' 978-0 '


@pytest.mark.django_db
def test_browser_lending_form_preserves_padded_member_and_isbn(client):
    response = client.post(
        '/ui/loans/new/',
        {'member': ' m1 ', 'isbn': ' 978-0 '},
        follow=True,
    )

    assert response.status_code == 200
    assert response.redirect_chain == [('/ui/loans/L4/', 302)]
    assert b' m1  \xc2\xb7 ISBN  978-0 ' in response.content
    loan = Loan.objects.get(pk='L4')
    assert loan.member == ' m1 '
    assert loan.isbn == ' 978-0 '


@pytest.mark.django_db
@pytest.mark.parametrize(
    ('path', 'payload', 'field', 'status'),
    [
        ('/loans', {'member': ' ', 'isbn': '978-0'}, 'member', 400),
        ('/loans', {'member': 'm1', 'isbn': '  '}, 'isbn', 400),
        ('/ui/loans/new/', {'member': ' ', 'isbn': '978-0'}, 'member', 200),
        ('/ui/loans/new/', {'member': 'm1', 'isbn': '  '}, 'isbn', 200),
    ],
)
def test_lending_rejects_whitespace_only_values(client, path, payload, field, status):
    response = client.post(path, payload)

    assert response.status_code == status
    assert field.encode() in response.content
    assert Loan.objects.count() == 3
