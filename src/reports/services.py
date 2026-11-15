from dataclasses import dataclass


@dataclass
class MemberReport:
    member_id: str
    loans_started: int = 0
    late_returns: int = 0
    late_fees_cents: int = 0


class MonthlyReport:
    def __init__(self, loans, fees):
        self.loans = loans
        self.fees = fees

    def for_period(self, start, end):
        members = {}
        for loan in self.loans.started_between(start, end):
            report = members.setdefault(loan.member, MemberReport(loan.member))
            report.loans_started += 1

        for loan in self.loans.returned_between(start, end):
            report = members.get(loan.member)
            if report is None:
                continue
            fee = self.fees.fee_for(loan.id)
            if fee is None:
                continue
            report.late_returns += fee.days_late > 0
            report.late_fees_cents += fee.amount_cents

        return sorted(
            members.values(),
            key=lambda report: (-report.late_fees_cents, report.member_id),
        )
