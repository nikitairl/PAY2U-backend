from django.contrib import admin

from .models import Document, Payment, CashbackApplied


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "text")


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("id", "amount", "date", "receipt")


@admin.register(CashbackApplied)
class CashbackAppliedAdmin(admin.ModelAdmin):
    list_display = ("id", "amount", "applied_status")
