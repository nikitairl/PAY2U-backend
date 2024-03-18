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
        verbose_name = "План подписки"
        verbose_name_plural = "Планы подписки"

    def __str__(self):
        return self.name


class AccessCode(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=50, default="Код доступа")
    end_date = models.DateTimeField(default=None)
    status = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Код доступа"
        verbose_name_plural = "Коды доступа"

    def __str__(self):
        return self.name


class UserSubscription(models.Model):
    id = models.BigAutoField(primary_key=True)
    status = models.BooleanField(default=True)
    activation = models.BooleanField(default=True)
    start = models.DateTimeField()
    end = models.DateTimeField()
    trial = models.BooleanField()
    user_id = models.ForeignKey(
        "users.User",
        on_delete=models.RESTRICT,
        related_name="user_subscription",
    )
    subscription = models.ForeignKey(
        "subscriptions.Subscription",
        on_delete=models.RESTRICT,
        related_name="user_subscription",
    )
    access_code = models.ForeignKey(
        AccessCode,
        on_delete=models.RESTRICT,
        related_name="user_subscription",
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = "Подписка пользователя"
        verbose_name_plural = "Подписки пользователей"

    def __str__(self):
        return str(self.id)
