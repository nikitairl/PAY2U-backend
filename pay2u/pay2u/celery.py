import os

from celery import Celery
from celery.schedules import crontab


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pay2u.settings")

app = Celery("pay2u")

app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

app.conf.beat_schedule = {
    "check_expired_subscriptions": {
        "task": "pay2u.worker.check_expired_subscriptions",
        "schedule": crontab(
            minute="*/5",
            hour="*",
            day_of_week="*",
            day_of_month="*",
            month_of_year="*",
        ),
    },
}
