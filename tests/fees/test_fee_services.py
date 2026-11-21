from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal

from src.fees.services import FeeApplication, PaymentApplication


@dataclass
class FeeLoan:
    id: str
    lent_on: date
    returned_on: date | None = None

    @property
    def due_on(self):
        return self.lent_on + timedelta(days=14)


class InMemoryFeeRepository:
    def __init__(self, loan):
        self.loan = loan

    def find(self, loan_id):
        return self.loan if self.loan is not None and self.loan.id == loan_id else None


class FixedClock:
    def today(self):
        return date(2026, 1, 22)


def test_fee_calculation_waives_first_two_late_days():
    repository = InMemoryFeeRepository(FeeLoan(id='L1', lent_on=date(2026, 1, 1)))

    fee = FeeApplication(repository, FixedClock()).calculate('L1')

    assert fee is not None
    assert fee.late_days == 7
    assert fee.amount == Decimal('1.75')


def test_fee_calculation_caps_at_ten_dollars():
    repository = InMemoryFeeRepository(FeeLoan(id='L1', lent_on=date(2025, 10, 1)))

    fee = FeeApplication(repository, FixedClock()).calculate('L1')

    assert fee is not None
    assert fee.amount == Decimal('10.00')


def test_unknown_fee_is_rejected_by_use_case():
    application = FeeApplication(InMemoryFeeRepository(None), FixedClock())

    assert application.calculate('unknown') is None


def test_fee_calculation_waives_exactly_two_late_days():
    repository = InMemoryFeeRepository(
        FeeLoan(id='L1', lent_on=date(2026, 1, 1), returned_on=date(2026, 1, 17))
    )

    fee = FeeApplication(repository, FixedClock()).calculate('L1')

    assert fee is not None
    assert fee.late_days == 2
    assert fee.amount == Decimal('0.00')


def test_fee_calculation_charges_three_late_days_at_twenty_five_cents():
    repository = InMemoryFeeRepository(
        FeeLoan(id='L1', lent_on=date(2026, 1, 1), returned_on=date(2026, 1, 18))
    )

    fee = FeeApplication(repository, FixedClock()).calculate('L1')

    assert fee is not None
    assert fee.late_days == 3
    assert fee.amount == Decimal('0.75')


def test_unknown_payment_is_rejected_before_gateway_call():
    gateway_calls = []

    class RecordingGateway:
        def charge(self, loan_id):
            gateway_calls.append(loan_id)
            return 200, 'charged'

    application = PaymentApplication(InMemoryFeeRepository(None), RecordingGateway())

    outcome, status, body = application.pay('unknown')

    assert outcome == 'missing'
    assert status == 404
    assert body == 'no such loan\n'
    assert gateway_calls == []


def test_interrupted_payment_is_surface_as_gateway_failure():
    class InterruptedGateway:
        def charge(self, loan_id):
            raise InterruptedError('caller cancelled')

    repository = InMemoryFeeRepository(FeeLoan(id='L1', lent_on=date(2026, 1, 1)))
    application = PaymentApplication(repository, InterruptedGateway())

    outcome, status, body = application.pay('L1')

    assert outcome == 'failure'
    assert status == 502
    assert body == 'payment gateway unavailable\n'


def test_payment_application_maps_gateway_success_and_failure():
    class Gateway:
        def __init__(self, status, body):
            self.status = status
            self.body = body

        def charge(self, loan_id):
            return self.status, self.body

    repository = InMemoryFeeRepository(FeeLoan(id='L1', lent_on=date(2026, 1, 1)))

    success = PaymentApplication(repository, Gateway(200, 'charged')).pay('L1')
    failure = PaymentApplication(repository, Gateway(503, 'declined')).pay('L1')

    assert success == ('success', 200, 'charged')
    assert failure == ('failure', 502, 'declined')
