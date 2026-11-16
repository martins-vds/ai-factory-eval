import pytest


@pytest.mark.django_db
@pytest.mark.parametrize(
    ('member', 'isbn'),
    [
        ('', '9780134685991'),
        ('   ', '9780134685991'),
        ('reader', ''),
        ('reader', '   '),
    ],
)
def test_lend_api_rejects_blank_member_and_isbn(client, member, isbn):
    response = client.post('/loans', {'member': member, 'isbn': isbn})

    assert response.status_code == 400
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == 'member and isbn are required\n'
