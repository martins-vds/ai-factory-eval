from src.loans.repository import DjangoLoanRepository

from .payments import HttpPaymentGateway, PaymentApplication

payment_application = PaymentApplication(DjangoLoanRepository(), HttpPaymentGateway())
