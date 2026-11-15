import json
from pathlib import Path

ABOUT_GOLDEN_PATH = (
    Path(__file__).resolve().parents[2] / '.migration/characterization/source/goldens/http.json'
)
ABOUT_GOLDEN = json.loads(ABOUT_GOLDEN_PATH.read_text(encoding='utf-8'))['GET /about']['response']


def test_about_endpoint_matches_characterized_html(client):
    response = client.get('/about')

    assert response.status_code == ABOUT_GOLDEN['status']
    assert response['Content-Type'] == ABOUT_GOLDEN['content_type']
    assert response.content.decode() == ABOUT_GOLDEN['body']
