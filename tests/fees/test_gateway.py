from src.fees.gateway import HttpPaymentGateway


class GatewayResponse:
    status = 200

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception, traceback):
        return False

    def read(self):
        return b'\xff'


class GatewayOpener:
    def open(self, request):
        self.request = request
        return GatewayResponse()


def test_payment_gateway_uses_legacy_default_and_replaces_invalid_utf8(monkeypatch):
    opener = GatewayOpener()
    monkeypatch.delenv('PAYMENT_GATEWAY_URL', raising=False)
    monkeypatch.setattr('src.fees.gateway.build_opener', lambda handler: opener)

    response = HttpPaymentGateway().charge('L1')

    assert opener.request.full_url == ('https://payments.lending-library.invalid/charge?loan=L1')
    assert opener.request.get_method() == 'POST'
    assert (response.status, response.body) == (200, '\ufffd')
