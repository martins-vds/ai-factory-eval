import json
from pathlib import Path

from django.test import TestCase

HTTP_GOLDEN_PATH = (
    Path(__file__).resolve().parents[2] / '.migration/characterization/source/goldens/http.json'
)


class AboutPageTests(TestCase):
    def test_about_endpoint_matches_characterized_html(self):
        expected = json.loads(HTTP_GOLDEN_PATH.read_text(encoding='utf-8'))['GET /about'][
            'response'
        ]

        response = self.client.get('/about')

        self.assertEqual(response.status_code, expected['status'])
        self.assertEqual(response['Content-Type'], expected['content_type'])
        self.assertEqual(response.content.decode(), expected['body'])
