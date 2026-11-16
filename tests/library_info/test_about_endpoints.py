import json
from pathlib import Path

HTTP_GOLDEN_PATH = (
    Path(__file__).resolve().parents[2] / '.migration/characterization/source/goldens/http.json'
)


def test_about_endpoint_matches_characterized_response(client):
    expected = json.loads(HTTP_GOLDEN_PATH.read_text(encoding='utf-8'))['GET /about']['response']

    response = client.get('/about')

    assert response.status_code == expected['status']
    assert response['Content-Type'] == expected['content_type']
    assert response.content.decode() == expected['body']
