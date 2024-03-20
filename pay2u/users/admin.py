from django.contrib import admin

from .models import User, Account


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    pass


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ("id", "account_number", "user", "balance")
