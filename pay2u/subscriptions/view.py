from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from api.serializers import (
    MainPageSerializer,
    UserPaymentsPlanSerializer,
    UserSubscriptionSerializer,
    UserSubscriptionsSerializer
)
from .models import UserSubscription, Subscription


class ActiveUserSubscriptionView(APIView):
    def get(self, request, user_id: int) -> Response:
        """
        Метод получения данных о карточке активной подписки.

        Параметры:
            user_id: идентификатор пользователя

        Возвращает:
            Данные о всех неактивных подписках пользователя.
        """
        try:
            user_subscription = UserSubscription.objects.select_related(
                "subscription__service_id"
            ).filter(user_id=user_id, status=True)
        except Subscription.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        subscription_data = UserSubscriptionSerializer(
            user_subscription, many=True, read_only=True
        ).data
        return Response(subscription_data, status=status.HTTP_200_OK)


class MainPageView(APIView):  # ДОДЕЛАТЬ (один запрос в бд)
    def get(self, request, user_id):
        """
        Метод получения данных для главного экрана приложения.

        Параметры:
            user_id: идентификатор пользователя

        Возвращает:
            Данные для главного экрана приложения.
        """
        try:
            active_subs = (
                UserSubscription.objects.filter(user_id=user_id, status=True)
                .select_related(
                    "subscription",
                    "subscription__service_id",
                    "subscription__trial_period",
                )
                .order_by("end")
            )
            active_subs_data = MainPageSerializer(active_subs, many=True).data
            return Response(active_subs_data, status=status.HTTP_200_OK)
        except UserSubscription.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class NonActiveUserSubscriptionView(APIView):
    def get(self, request, user_id: int) -> Response:
        """
        Метод получения данных о карточке активной подписки.

        Параметры:
            user_id: идентификатор пользователя

        Возвращает:
            Данные о всех неактивных подписках пользователя.
        """
        try:
            user_subscription = UserSubscription.objects.select_related(
                "subscription__service_id"
            ).filter(user_id=user_id, status=False)
        except Subscription.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        subscription_data = UserSubscriptionSerializer(
            user_subscription, many=True, read_only=True
        ).data
        return Response(subscription_data, status=status.HTTP_200_OK)


class ServiceUserSubscriptionsView(APIView):
    def get(self, request, user_id: int, service_id: int) -> Response:
        """
        Метод получения данных о всех подписках пользователя по сервису.

        Параметры:
            user_id: идентификатор пользователя
            service_id: идентификатор сервиса

        Возвращает:
            Данные о всех подписках пользователя по сервису.
        """
        try:
            user_subscriptions = UserSubscription.objects.filter(
                user_id=user_id, subscription__service_id=service_id).first()
        except UserSubscription.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        subscription_data = UserSubscriptionSerializer(
            user_subscriptions, read_only=True).data
        return Response(subscription_data, status=status.HTTP_200_OK)


class UserSubscriptionView(APIView):
    def get(self, request, subscription_id: int) -> Response:
        """
        Метод получения данных о карточке активной подписки.

        Параметры:
            subscription_id: идентификатор активной подписки пользователя

        Возвращает:
            Данные о карточке активной подписки пользователя.
        """
        try:
            user_subscription = (
                UserSubscription.objects.select_related(
                    "subscription__service_id"
                )
                .filter(user_id=request.user, id=subscription_id)
                .first()
            )
        except UserSubscription.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        subscription_data = UserSubscriptionSerializer(user_subscription).data
        return Response(subscription_data, status=status.HTTP_200_OK)


class UserSubscriptionRenewalView(APIView):
    def patch(self, request, user_subscription_id: int):
        """
        Метод изменения статуса активной подписки.
        Изменяет статус renewal в UserSubscription

        Параметры:
            user_subscription_id: идентификатор активной подписки
        Тело запроса:
            {
                "renewal": "<bool>"
            }

        Returns:
            Измененные данные активной подписки.
        """
        try:
            user_subscription = UserSubscription.objects.get(
                id=user_subscription_id
            )
        except UserSubscription.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        data = {
            "renewal": request.data.get("renewal"),
        }
        serializer = UserSubscriptionSerializer(
            user_subscription, data=data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserSubscriptionsView(APIView):
    def get(self, request, user_id: int) -> Response:
        """
        Метод получения данных о карточке активной подписки.

        Параметры:
            user_id: идентификатор пользователя

        Возвращает:
            Данные о всех подписках пользователя.
        """
        try:
            user_subscriptions = UserSubscription.objects.select_related(
                "subscription__service_id"
            ).filter(user_id=user_id).order_by("status")
        except UserSubscription.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        subscription_data = UserSubscriptionsSerializer(
            user_subscriptions, many=True, read_only=True
        ).data
        return Response(subscription_data, status=status.HTTP_200_OK)


class UserPaymentsPlanView(APIView):
    def get(self, request, user_id: int):
        """
        Метод получения данных о ближайших платежах пользователя.

        Параметры:
            user_id: идентификатор пользователя

        Возвращает:
            Данные о всех ближайших платежах пользователя.
        """
        try:
            upcoming_payments = UserSubscription.objects.filter(
                user_id=user_id
            ).order_by("-end")
        except Subscription.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        upcoming_payments_data = UserPaymentsPlanSerializer(
            upcoming_payments, many=True, read_only=True
        ).data
        return Response(upcoming_payments_data, status=status.HTTP_200_OK)
