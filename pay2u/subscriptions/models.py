from django.db import models

from .constants import SUB_METHODS


class Subscription(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=50)
    availability = models.BooleanField()
    price = models.IntegerField()
    period = models.IntegerField()
    cashback = models.IntegerField()
    service_id = models.ForeignKey(
        "services.Service",
        on_delete=models.CASCADE
    )
    trial_period = models.IntegerField()
    activation_method = models.CharField(max_length=20, choices=SUB_METHODS)

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"

    def __str__(self):
        return self.name


class AccessCode(models.Model):
    pass
