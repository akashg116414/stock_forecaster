from django.apps import AppConfig
from core import settings


class AppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app'

    def ready(self):
        if settings.SCHEDULER_AUTOSTART:
            from core import operator
            operator.start()