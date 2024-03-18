from django.db import models

from .constants import SUB_METHODS


class TrialPeriod(models.Model):
    id = models.BigAutoField(primary_key=True)
    period_days = models.IntegerField('Срок пробного периода', default=0)
    period_cost = models.IntegerField('Стоимость пробного периода', default=0)

    class Meta:
        verbose_name = "Пробная подписка"
        verbose_name_plural = "Пробные подписки"

    def __str__(self):
        return str(f'{self.id} - {self.period_days}, {self.period_cost}р.')


class Subscription(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=50, unique=True)
    availability = models.BooleanField()
    price = models.IntegerField()
    period = models.IntegerField()
    cashback = models.IntegerField()
    service_id = models.ForeignKey(
        "services.Service",
        on_delete=models.RESTRICT,
        related_name="subscription",
    )
    trial_period = models.ForeignKey(
        TrialPeriod,
        on_delete=models.RESTRICT,
        blank=True,
        null=True,
    )
    activation_method = models.CharField(max_length=20, choices=SUB_METHODS)

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"

    def __str__(self):
        return self.name


class AccessCode(models.Model):
    pass
