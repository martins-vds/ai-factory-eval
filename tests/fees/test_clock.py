from datetime import date

from src.fees.clock import ServerLocalClock


def test_fee_clock_uses_the_server_local_date(monkeypatch):
    from django.utils import timezone

    monkeypatch.setattr(timezone, 'localdate', lambda: date(2000, 1, 1))

    assert ServerLocalClock().today() == date.today()
