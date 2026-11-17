def test_about_endpoint_matches_characterized_response(client):
    response = client.get('/about')

    assert response.status_code == 200
    assert response['Content-Type'].split(';', maxsplit=1)[0] == 'text/html'
    assert response.content.decode() == (
        '<!doctype html>\n'
        '<html lang="en">\n'
        '<head><meta charset="utf-8"><title>About the Lending Library</title></head>\n'
        '<body>\n'
        '  <h1>About the Lending Library</h1>\n'
        '  <p>Open Monday to Saturday, 9:00 to 18:00. Books are lent for 14 days.</p>\n'
        '  <p>Contact: desk@lending-library.invalid</p>\n'
        '</body>\n'
        '</html>\n'
    )
