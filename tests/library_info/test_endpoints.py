import json
from pathlib import Path


HTTP_GOLDENS = json.loads(
    (
        Path(__file__).resolve().parents[2]
        / '.migration/characterization/source/goldens/http.json'
    ).read_text(encoding='utf-8')
)


def test_about_endpoint_matches_characterized_response(client):
    expected = HTTP_GOLDENS['GET /about']['response']

    response = client.get('/about')

    assert response.status_code == expected['status']
    assert response['Content-Type'] == expected['content_type']
    assert response.content.decode() == expected['body']
