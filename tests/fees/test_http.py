import json
from pathlib import Path

import pytest

GOLDENS = Path(__file__).resolve().parents[2] / '.migration/characterization/source/goldens'
HTTP_GOLDENS = json.loads((GOLDENS / 'http.json').read_text(encoding='utf-8'))
EDGE_GOLDENS = json.loads((GOLDENS / 'edge-cases.json').read_text(encoding='utf-8'))


@pytest.mark.django_db
def test_fee_endpoint_matches_characterized_page(client):
    expected = HTTP_GOLDENS['GET /fees/{id}']['response']

    response = client.get('/fees/L3')

    assert response.status_code == expected['status']
    assert response['Content-Type'].split(';')[0] == expected['content_type']
    assert response.content.decode() == expected['body']


@pytest.mark.django_db
def test_fee_endpoint_matches_characterized_missing_loan_response(client):
    expected = EDGE_GOLDENS['GET /fees/unknown']['response']

    response = client.get('/fees/unknown')

    assert response.status_code == expected['status']
    assert response['Content-Type'].split(';')[0] == expected['content_type']
    assert response.content.decode() == expected['body']
