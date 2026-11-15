import os
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

DEFAULT_GATEWAY_URL = 'https://payments.lending-library.invalid'


class PaymentGatewayFailure(Exception):
    pass


class PaymentGatewayInterrupted(PaymentGatewayFailure):
    pass


class PaymentGateway:
    def charge(self, loan_id):
        gateway_url = os.environ.get('PAYMENT_GATEWAY_URL', DEFAULT_GATEWAY_URL)
        request = Request(f'{gateway_url}/charge?loan={loan_id}', method='POST')
        try:
            with urlopen(request) as response:
                return response.status, response.read()
        except HTTPError as response:
            try:
                return response.code, response.read()
            finally:
                response.close()
        except InterruptedError as error:
            raise PaymentGatewayInterrupted from error
        except URLError as error:
            if isinstance(error.reason, InterruptedError):
                raise PaymentGatewayInterrupted from error.reason
            raise PaymentGatewayFailure from error
        except OSError as error:
            raise PaymentGatewayFailure from error
