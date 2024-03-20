from django.db import models


class Document(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=30)
    text = models.TextField(max_length=1000)

    class Meta:
        verbose_name = "Документ"
        verbose_name_plural = "Документы"

    def __str__(self):
        return str(self.id)


class CashbackApplied(models.Model):
    id = models.BigAutoField(primary_key=True)
    amount = models.IntegerField()
    applied_status = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Кэшбэк"
        verbose_name_plural = "Кэшбэки"

    def __str__(self):
        return str(self.amount)


def increment_receipt_number():
    last_invoice = Payment.objects.all().order_by('id').last()
    if not last_invoice:
        return 'R000001'
    receipt_no = last_invoice.receipt
    receipt_int = int(receipt_no.split('R')[-1])
    new_receipt_int = receipt_int + 1
    new_receipt_no = 'R' + str(new_receipt_int).zfill(4)
    return new_receipt_no


class Payment(models.Model):
    id = models.BigAutoField(primary_key=True)
    amount = models.IntegerField(null=False)
    date = models.DateTimeField(auto_now_add=True)
    receipt = models.CharField(
        max_length=500,
        default=increment_receipt_number,
        unique=True,
    )
    document = models.ForeignKey(
        Document,
        on_delete=models.SET("DELETED"),
        related_name="payments",
        null=False,
        blank=False,
    )
    cashback_applied = models.ForeignKey(
        CashbackApplied,
        on_delete=models.RESTRICT,
        related_name="payments",
        null=False,
        blank=False,
    )
    user_subscription = models.ForeignKey(
        "subscriptions.Subscription",
        on_delete=models.SET("DELETED"),
        related_name="payments",
        null=False,
        blank=False,
    )
    account_id = models.ForeignKey(
        "users.Account",
        on_delete=models.SET("DELETED"),
        related_name="payments",
        null=False,
        blank=False,
    )

    class Meta:
        verbose_name = "Платеж"
        verbose_name_plural = "Платежи"

    def __str__(self):
        return self.receipt
