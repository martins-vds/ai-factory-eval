def test_legacy_about_response_matches_characterization(client):
    response = client.get('/about')

    assert response.status_code == 200
    assert response['Content-Type'] == 'text/html'
    assert response.content == (
        b'<!doctype html>\n'
        b'<html lang="en">\n'
        b'<head><meta charset="utf-8"><title>About the Lending Library</title></head>\n'
        b'<body>\n'
        b'  <h1>About the Lending Library</h1>\n'
        b'  <p>Open Monday to Saturday, 9:00 to 18:00. Books are lent for 14 days.</p>\n'
        b'  <p>Contact: desk@lending-library.invalid</p>\n'
        b'</body>\n'
        b'</html>\n'
    )
