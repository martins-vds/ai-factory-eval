import json
from pathlib import Path

import pytest

HTTP_GOLDEN_PATH = (
    Path(__file__).resolve().parents[2] / '.migration/characterization/source/goldens/http.json'
)
HTTP_GOLDENS = json.loads(HTTP_GOLDEN_PATH.read_text(encoding='utf-8'))


@pytest.mark.django_db
def test_about_response_matches_characterization(client):
    response = client.get('/about')
    expected = HTTP_GOLDENS['GET /about']['response']

    assert response.status_code == expected['status']
    assert response['Content-Type'] == expected['content_type']
    assert response.content.decode() == expected['body']
