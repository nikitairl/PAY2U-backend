from datetime import timezone
from .celery import app

from subscriptions.models import UserSubscription


@app.task
def check_expired_subscriptions():
    subscriptions = UserSubscription.objects.filter(status=True)
    for subscription in subscriptions:
        if subscription.end < timezone.now():
            subscription.status = False
            subscription.save()
            print("status changed")
        print(subscription)
    return "task done"
