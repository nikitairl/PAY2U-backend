from django.db import models


class Bank(models.Model):
    id = models.BigAutoField(primary_key=True)
    inn = models.IntegerField(
        unique=True, null=False, blank=False, verbose_name="ИНН"
    )

    class Meta:
        verbose_name = "Банк"
        verbose_name_plural = "Банки"

    def __str__(self):
        return str(self.inn)


class BankUser(models.Model):
    id = models.BigAutoField(primary_key=True)
    bank_id = models.ForeignKey(
        Bank,
        on_delete=models.CASCADE,
        related_name="bank_user",
        null=False,
        blank=False,
    )
    user_id = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="bank_user",
        null=False,
        blank=False,
    )

    class Meta:
        verbose_name = "Пользователь банка"
        verbose_name_plural = "Пользователи банков"

    def __str__(self):
        return str(self.user_id)
