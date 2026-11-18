from datetime import date

from django.utils import timezone


class SystemClock:
    def today(self) -> date:
        return timezone.localdate(timezone.now(), timezone.get_default_timezone())
