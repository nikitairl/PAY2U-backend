from django.contrib import admin

from .models import Bank, BankUser


@admin.register(Bank)
class BankAdmin(admin.ModelAdmin):
    list_display = ("id", "inn")


@admin.register(BankUser)
class BankUserAdmin(admin.ModelAdmin):
    list_display = ("id", "bank_id", "user_id")
