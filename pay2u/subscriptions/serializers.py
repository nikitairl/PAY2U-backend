from rest_framework import serializers

from services.serializers import ServiceSerializer
from .models import AccessCode, Subscription, TrialPeriod, UserSubscription


class AccessCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccessCode
        fields = ("name", "end_date")


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
    popularity = serializers.IntegerField(source="service_id__popularity")

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
            "popularity",
        )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if data["trial_period_days"] is None:
            data.pop("trial_period_days")
            data.pop("trial_period_cost")
        return data


class TrialPeriodSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrialPeriod
        fields = ("period_cost", "period_days")


class SubscriptionSerializer(serializers.ModelSerializer):
    service = ServiceSerializer(read_only=True, source="service_id")
    trial = TrialPeriodSerializer(read_only=True, source="trial_period")

    class Meta:
        model = Subscription
        fields = (
            "id",
            "name",
            "availability",
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


class UserSubscriptionsSerializer(serializers.ModelSerializer):
    user_subscription = SubscriptionSerializer(read_only=True,
                                               source="subscription")

    class Meta:
        model = UserSubscription
        fields = (
            "user_subscription",
            "id",
            "status",
            "renewal",
            "end",
        )


class UserPaymentsPlanSerializer(serializers.ModelSerializer):
    service = ServiceSerializer(
        read_only=True, source="subscription.service_id"
    )
    user_subscription_cost = serializers.IntegerField(
        source="subscription.price"
    )

    class Meta:
        model = UserSubscription
        fields = (
            "user_subscription_cost",
            "service",
            "end"
        )
