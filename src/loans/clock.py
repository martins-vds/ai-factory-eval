from django.utils import timezone


class DjangoClock:
    def today(self):
        return timezone.localdate()
