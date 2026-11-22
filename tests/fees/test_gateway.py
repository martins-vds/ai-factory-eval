from unittest.mock import patch

import pytest

from src.fees.gateway import HttpPaymentGateway
from src.fees.services import FeeApplication, GatewayUnavailable


def test_gateway_posts_empty_body_and_preserves_gateway_response(payment_server):
    gateway = HttpPaymentGateway(f'http://127.0.0.1:{payment_server.server_port}')

    response = gateway.charge('L1')

    assert payment_server.requests == [('POST', '/charge?loan=L1', b'')]
    assert (response.status_code, response.body) == (200, 'charged\n')


def test_payment_maps_non_200_gateway_response_to_502_and_preserves_body(payment_server):
    payment_server.response_status = 503
    payment_server.response_body = b'declined\n'
    gateway = HttpPaymentGateway(f'http://127.0.0.1:{payment_server.server_port}')
    application = FeeApplication(
        repository=LoanRepository(),
        clock=None,
        gateway=gateway,
    )

    response = application.pay('L1')

    assert (response.status_code, response.body) == (502, 'declined\n')


def test_interrupted_gateway_call_is_reported_without_losing_interruption():
    gateway = HttpPaymentGateway('http://127.0.0.1:1')

    with patch('src.fees.gateway.urlopen', side_effect=InterruptedError('interrupted')):
        with pytest.raises(GatewayUnavailable) as failure:
            gateway.charge('L1')

    assert isinstance(failure.value.__cause__, InterruptedError)


class LoanRepository:
    def find(self, loan_id):
        return object()
