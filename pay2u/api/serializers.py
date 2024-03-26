from rest_framework import serializers

from payments.models import Document
from payments.models import Payment, CashbackApplied
from services.models import Service
from subscriptions.models import (AccessCode, Subscription, UserSubscription,
                                  TrialPeriod)
from users.models import Account


class AccessCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccessCode
        fields = ("name", "end_date")


class TrialPeriodSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrialPeriod
        fields = ("period_cost", "period_days")


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ("id", "image", "name")


class SubscriptionSerializer(serializers.ModelSerializer):
    service = ServiceSerializer(read_only=True, source="service_id")
    trial = TrialPeriodSerializer(read_only=True, source="trial_period")

    class Meta:
        model = Subscription
        fields = (
            "id",
            "name",
            "price",
            "period",
            "cashback",
            "trial",
            "service"
        )


class MainPageSerializer(serializers.ModelSerializer):
    subscription = SubscriptionSerializer(read_only=True)

    class Meta:
        model = UserSubscription
        fields = (
            "id",
            "status",
            "activation",
            "renewal",
            "start",
            "end",
            "trial",
            "subscription",
        )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        subscription_data = {"user_subscription": data}
        return subscription_data


class PaymentsAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ("id", "account_number")


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ("id", "account_number", "account_status")


class CashbackAppliedSerializer(serializers.ModelSerializer):
    class Meta:
        model = CashbackApplied
        fields = ("id", "amount", "applied_status")


class PaymentsSerializer(serializers.ModelSerializer):
    service = ServiceSerializer(
        read_only=True, source="user_subscription.service_id"
    )
    account = PaymentsAccountSerializer(read_only=True, source="account_id")
    cashback = CashbackAppliedSerializer(
        read_only=True, source="cashback_applied"
    )

    class Meta:
        model = Payment
        fields = (
            "id",
            "date",
            "amount",
            "service",
            "account",
            "cashback",
        )


class UserSubscriptionSerializer(serializers.ModelSerializer):
    access_code = AccessCodeSerializer()
    user_subscription = SubscriptionSerializer(read_only=True,
                                               source="subscription")

    class Meta:
        model = UserSubscription
        fields = (
            "user_subscription",
            "renewal",
            "end",
            "trial",
            "access_code"
        )


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ("name", "text")


class AvailableServiceSerializer(serializers.ModelSerializer):
    min_subscription_cost = serializers.IntegerField(source="price__min")
    service_name = serializers.StringRelatedField(source="service_id__name")
    image = serializers.StringRelatedField(source="service_id__image")
    trial_period_days = serializers.IntegerField(
        source="trial_period__period_days"
    )
    trial_period_cost = serializers.IntegerField(
        source="trial_period__period_cost"
    )
    category_id = serializers.IntegerField(source="service_id__category_id")
    category_name = serializers.StringRelatedField(
        source="service_id__category_id__name"
    )

    class Meta:
        model = Subscription
        fields = (
            "service_name",
            "image",
            "min_subscription_cost",
            "period",
            "cashback",
            "trial_period_days",
            "trial_period_cost",
            "category_id",
            "category_name",
        )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if data["trial_period_days"] is None:
            data.pop("trial_period_days")
            data.pop("trial_period_cost")
        return data
