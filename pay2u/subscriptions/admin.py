from django.contrib import admin

from .models import Subscription, TrialPeriod, AccessCode, UserSubscription


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("name", "availability", "price", "period", "cashback")


@admin.register(TrialPeriod)
class TrialPeriodAdmin(admin.ModelAdmin):
    list_display = ("period_days", "period_cost")


@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display = ("id", "status", "subscription_id", "subscription", "user_id")


@admin.register(AccessCode)
class AccessCodeAdmin(admin.ModelAdmin):
    list_display = ("name", "end_date", "status")
