import os
import socket
import subprocess
import sys
import time
from contextlib import contextmanager
from datetime import date
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

import pytest
from django.db import connection

from src.loans.models import Loan
from src.loans.repository import create_loan


@contextmanager
def running_server(port, environment):
    process = subprocess.Popen(
        [sys.executable, 'manage.py', 'runserver', f'127.0.0.1:{port}', '--noreload'],
        env=environment,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        yield process
    finally:
        process.terminate()
        process.wait(timeout=10)


def loan_response(port, loan_id):
    url = f'http://127.0.0.1:{port}/loans/{loan_id}'
    last_error = None
    for _ in range(50):
        try:
            with urlopen(url, timeout=1) as response:
                return response.status, response.read().decode()
        except HTTPError as response:
            return response.code, response.read().decode()
        except URLError as error:
            last_error = error
            time.sleep(0.1)
    raise AssertionError(f'Application did not start: {last_error}')


@pytest.mark.django_db
def test_catalog_list_and_lookup_match_characterized_output(client):
    response = client.get('/loans')

    assert response.status_code == 200
    assert response['Content-Type'].startswith('text/plain')
    assert response.content.decode() == (
        'L1;ana;9780134685991;2026-01-02;2026-01-16;\n'
        'L2;bo;9780596007126;2026-01-10;2026-01-24;2026-01-20\n'
        'L3;cy;9781617294945;2025-12-01;2025-12-15;2026-01-03\n'
    )

    detail = client.get('/loans/L1')
    assert detail.status_code == 200
    assert detail['Content-Type'].startswith('text/plain')
    assert detail.content.decode() == 'L1;ana;9780134685991;2026-01-02;2026-01-16;\n'


@pytest.mark.django_db
def test_unknown_loan_returns_characterized_not_found_response(client):
    response = client.get('/loans/unknown')

    assert response.status_code == 404
    assert response['Content-Type'].startswith('text/plain')
    assert response.content.decode() == 'no such loan\n'


@pytest.mark.django_db
def test_catalog_orders_loan_records_by_identifier(client):
    create_loan(loan_id='L9', member='Reader 9', isbn='9', lent_on=date(2026, 1, 1))
    create_loan(loan_id='L4', member='Reader 4', isbn='4', lent_on=date(2026, 1, 1))

    response = client.get('/loans')

    loan_ids = [line.split(';', maxsplit=1)[0] for line in response.content.decode().splitlines()]
    assert loan_ids == ['L1', 'L2', 'L3', 'L4', 'L9']


@pytest.mark.django_db
def test_due_date_and_export_escape_delimiters(client):
    loan = create_loan(
        loan_id='L4',
        member='Reader; One',
        isbn='9780000000000',
        lent_on=date(2024, 2, 20),
    )

    assert loan.due_on == date(2024, 3, 5)
    response = client.get('/loans/L4')

    assert response.status_code == 200
    assert response.content.decode() == 'L4;"Reader; One";9780000000000;2024-02-20;2024-03-05;\n'


@pytest.mark.django_db
def test_browser_catalog_lists_and_displays_loan_details(client):
    listing = client.get('/ui/loans/')

    assert listing.status_code == 200
    assert b'Loan L1' in listing.content
    assert b'ana' in listing.content
    assert b'Due 2026-01-16' in listing.content
    assert b'href="/ui/loans/L1/"' in listing.content

    detail = client.get('/ui/loans/L1/')

    assert detail.status_code == 200
    assert b'9780134685991' in detail.content
    assert b'2026-01-16' in detail.content
    assert client.get('/ui/loans/unknown/').status_code == 404


@pytest.mark.django_db(transaction=True, serialized_rollback=True)
def test_loan_survives_application_restart_without_overwriting_seed_records():
    Loan.objects.filter(pk='L1').update(member='Persistent Reader')
    create_loan(
        loan_id='PERSISTED',
        member='Reader',
        isbn='9780000000000',
        lent_on=date(2026, 11, 1),
    )

    with socket.socket() as server_socket:
        server_socket.bind(('127.0.0.1', 0))
        port = server_socket.getsockname()[1]

    environment = os.environ.copy()
    database = connection.settings_dict
    environment.update(
        {
            'POSTGRES_DB': database['NAME'],
            'POSTGRES_USER': database['USER'],
            'POSTGRES_PASSWORD': database['PASSWORD'],
            'POSTGRES_HOST': database['HOST'],
            'POSTGRES_PORT': str(database['PORT']),
        }
    )

    for _ in range(2):
        with running_server(port, environment) as process:
            assert loan_response(port, 'PERSISTED') == (
                200,
                'PERSISTED;Reader;9780000000000;2026-11-01;2026-11-15;\n',
            )
            assert loan_response(port, 'L1') == (
                200,
                'L1;Persistent Reader;9780134685991;2026-01-02;2026-01-16;\n',
            )
            assert process.poll() is None
