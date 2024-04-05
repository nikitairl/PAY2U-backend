from datetime import datetime, timedelta

from django.db.models import Min
from django.middleware.csrf import get_token
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from services.models import Service
from subscriptions.models import UserSubscription, Subscription
from subscriptions.serializers import (
    AvailableServiceSerializer, UserSubscriptionSerializer
)
from users.models import Account, User
from .utils import query_min_price_sort


class CSRFTokenView(APIView):
    def get(self, request):
        """
        Метод получения токена CSRF.
        Postman use-case -  Headers: X-CSRFToken: <csrf_token>

        Возвращает:
            CSRF токен.
        """
        csrf_token = get_token(request)
        return Response({"csrf_token": csrf_token})


class AvailableServicesView(APIView):
    def get(self, request):
        """
        Метод получения доступных сервисов.

        Возвращает:
            Сервисы с тегом "available=True".
        """
        try:
            lowest_prices = (
                Subscription.objects.select_related("service_id")
                .select_related("trial_period")
                .values(
                    "service_id__name",
                    "service_id__image",
                    "period",
                    "cashback",
                    "trial_period__period_days",
                    "trial_period__period_cost",
                    "service_id__popularity",
                    "service_id__category_id",
                    "service_id__category_id__name",
                )
                .annotate(Min("price"))
                .order_by("service_id")
            )
            ser_data = AvailableServiceSerializer(
                query_min_price_sort(lowest_prices), many=True
            ).data
            return Response(ser_data, status=status.HTTP_200_OK)
        except Service.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class CategoriesView(APIView):
    def get(self, request, category_name: str):
        """
        Метод получения данных о сервисах по категории.

        Параметры:
            category_name: название категории

        Возвращает:
            Сервисы по указанной категории.
        """
        try:
            lowest_prices = (
                Subscription.objects.filter(
                    service_id__category__name=category_name
                )
                .select_related("service_id")
                .select_related("trial_period")
                .values(
                    "service_id__name",
                    "service_id__image",
                    "period",
                    "cashback",
                    "trial_period__period_days",
                    "trial_period__period_cost",
                    "service_id__popularity",
                    "service_id__category_id",
                    "service_id__category_id__name",
                )
                .annotate(Min("price"))
                .order_by("service_id")
            )
            ser_data = AvailableServiceSerializer(
                query_min_price_sort(lowest_prices), many=True
            ).data
            return Response(ser_data, status=status.HTTP_200_OK)
        except Service.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class ServiceView(APIView):
    def get(self, request, service_name: str):
        """
        Метод получения данных о сервисе по названию.

        Параметры:
            service_name: название сервиса

        Возвращает:
            Сервис по указанному названию.
        """
        try:
            lowest_prices = (
                Subscription.objects.filter(service_id__name=service_name)
                .select_related("service_id")
                .select_related("trial_period")
                .values(
                    "service_id__name",
                    "service_id__image",
                    "period",
                    "cashback",
                    "trial_period__period_days",
                    "trial_period__period_cost",
                    "service_id__popularity",
                    "service_id__category_id",
                    "service_id__category_id__name",
                    "service_id__popularity",
                )
                .annotate(Min("price"))
                .order_by("service_id")
            )
            ser_data = AvailableServiceSerializer(
                query_min_price_sort(lowest_prices), many=True
            ).data
            return Response(ser_data, status=status.HTTP_200_OK)
        except Service.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class AddUserSubscriptionView(APIView):
    def post(self, request, user_id):
        """
        Метод организации подписок для пользователя.
        Если подписка уже есть - продлевает.
        Если подписка уже есть, но другой тариф - заменяет.
        Если подписки нет - создает новую.
        """
        user = get_object_or_404(User, id=user_id)
        subscription_id = request.data.get("subscription_id")
        subscription = self.get_subscription_or_error(subscription_id)
        account_id = request.data.get("account_id")
        account_balance = get_object_or_404(Account, id=account_id)
        if not self.check_balance(subscription, account_balance):
            return Response({"error": "Недостаточно средств на счете."},
                            status=status.HTTP_400_BAD_REQUEST)
        active_subscription = self.get_active_subscription(
            user_id, subscription.service_id
        )
        if active_subscription:
            if active_subscription.subscription.id == subscription.id:
                self.extend_subscription(active_subscription, subscription)
            else:
                self.deactivate_subscription(active_subscription)
                new_subscription = self.create_new_subscription(
                    user, subscription, account_balance
                )
                return self.send_response(new_subscription)
        else:
            new_subscription = self.create_new_subscription(
                user, subscription, account_balance
            )
            return self.send_response(new_subscription)
        return self.send_response(active_subscription)

    def get_subscription_or_error(self, subscription_id):
        try:
            return Subscription.objects.get(id=subscription_id)
        except Subscription.DoesNotExist:
            raise ValidationError("Такой подписки не существует.")

    def check_balance(self, subscription, account_balance):
        if account_balance.balance - subscription.price >= 0:
            account_balance.balance -= subscription.price
            account_balance.save()
            return True
        return False

    def get_active_subscription(self, user_id, service):
        return UserSubscription.objects.filter(user_id=user_id,
                                               subscription__service_id=service,
                                               status=True).first()

    def extend_subscription(self, active_subscription, subscription):
        active_subscription.end += timedelta(days=subscription.period)
        active_subscription.status = True
        active_subscription.save()

    def deactivate_subscription(self, active_subscription):
        active_subscription.end = datetime.now()
        active_subscription.status = False
        active_subscription.renewal = False
        active_subscription.save()

    def create_new_subscription(self, user, subscription, account_balance):
        new_subscription = UserSubscription(
            user_id=user,
            subscription=subscription,
            status=True,
            renewal=True,
            activation=True,
            start=datetime.now(),
            end=datetime.now() + timedelta(days=subscription.period),
            trial=False
        )
        new_subscription.save()
        return new_subscription

    def send_response(self, subscription):
        serializer_data = UserSubscriptionSerializer(subscription).data
        return Response(serializer_data, status=status.HTTP_200_OK)
