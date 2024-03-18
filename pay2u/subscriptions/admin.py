from django.contrib import admin

from .models import Subscription, TrialPeriod


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("name", "availability", "price", "period", "cashback")
    pass


@admin.register(TrialPeriod)
class TrialPeriodAdmin(admin.ModelAdmin):
    list_display = ("period_days", "period_cost")
    pass
