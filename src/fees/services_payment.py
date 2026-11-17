from typing import Protocol

from .gateway import GatewayResponse
from .services import LoanRepository


class PaymentGateway(Protocol):
    def charge(self, loan_id: str) -> GatewayResponse: ...


class PaymentApplication:
    def __init__(self, repository: LoanRepository, gateway: PaymentGateway):
        self.repository = repository
        self.gateway = gateway

    def pay(self, loan_id: str) -> GatewayResponse | None:
        if self.repository.find(loan_id) is None:
            return None
        return self.gateway.charge(loan_id)
