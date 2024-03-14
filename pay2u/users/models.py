from django.db import models
from django.forms import BooleanField

from pay2u.subscriptions.models import Subscription, AccessCode


class User(models.Model):
    id = models.BigAutoField(primary_key=True)
    phone = models.CharField(max_length=20)
    email = models.EmailField()

    def __str__(self):
        return self.phone

    class Meta:
        db_table = "users"


class UserSubscription(models.Model):
    id = models.BigAutoField(primary_key=True)
    status = BooleanField(default=False)
    renewal = BooleanField(default=False)
    activation = BooleanField(default=False)
    subscription_date_start = models.DateTimeField()
    subscription_date_end = models.DateTimeField()
    users_id = models.ForeignKey(User, on_delete=models.CASCADE)
    subscription_plan = models.ForeignKey(
        Subscription, on_delete=models.RESTRICT
    )
    access_code = models.ForeignKey(
        AccessCode, on_delete=models.RESTRICT
    )
