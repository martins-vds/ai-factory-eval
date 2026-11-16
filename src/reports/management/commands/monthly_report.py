from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from src.reports.services import monthly_report, render_csv


class Command(BaseCommand):
    def handle(self, *args, **options):
        current_month = timezone.localdate().replace(day=1)
        previous_month = current_month - timedelta(days=1)
        start = previous_month.replace(day=1)
        self.stdout.write(render_csv(monthly_report(start, current_month)), ending='')
