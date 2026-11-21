from django.apps import AppConfig
from django.db.models.signals import post_migrate


def seed_loans(sender, **kwargs):
    from src.loans.models import seed_records_if_empty

    seed_records_if_empty()


class LoansConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'src.loans'

    def ready(self):
        post_migrate.connect(seed_loans, sender=self, dispatch_uid='loans.seed_records')
