from datetime import timedelta

import pytest
from django.utils import timezone


@pytest.mark.parametrize(
    'fields',
    [
        {'isbn': '123'},
        {'member': 'reader'},
        {'member': '', 'isbn': '123'},
        {'member': 'reader', 'isbn': ''},
        {'member': ' \t ', 'isbn': '123'},
        {'member': 'reader', 'isbn': ' \t '},
    ],
)
@pytest.mark.django_db
def test_lending_endpoint_rejects_missing_and_blank_fields(client, fields):
    response = client.post('/loans', fields)

    assert response.status_code == 400
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == 'member and isbn are required\n'


@pytest.mark.django_db
def test_lending_endpoint_creates_a_loan_with_fourteen_day_due_date(client):
    lent_on = timezone.localdate()

    response = client.post('/loans', {'member': 'dee', 'isbn': '123'})

    assert response.status_code == 201
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == (
        f'L4;dee;123;{lent_on.isoformat()};{(lent_on + timedelta(days=14)).isoformat()};\n'
    )
    assert client.get('/loans/L4').content == response.content


@pytest.mark.django_db
def test_lending_endpoint_escapes_delimiters_in_the_export(client):
    lent_on = timezone.localdate()

    response = client.post('/loans', {'member': 'a;b', 'isbn': '123;456'})

    assert response.status_code == 201
    assert response.content.decode() == (
        f'L4;"a;b";"123;456";{lent_on.isoformat()};'
        f'{(lent_on + timedelta(days=14)).isoformat()};\n'
    )
