from datetime import datetime

from django.db.models import Q, Min
from django.middleware.csrf import get_token
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from payments.models import Payment, Document
from subscriptions.models import UserSubscription, Subscription
from users.models import Account
from services.models import Service
from .serializers import (
    DocumentSerializer,
    MainPageSerializer,
    PaymentsSerializer,
    AccountSerializer,
    AvailableServiceSerializer,
    UserSubscriptionSerializer,
)
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


class PaymentsView(APIView):  # ГОТОВО (два запроса в бд)
    def get(self, request, user_id: int) -> Response:
        """
        Метод получения данных о платежах для указанного пользователя.

        Параметры:
            user_id: идентификатор пользователя

        Возвращает:
            Данные о платежах по указанному идентификатору пользователя.
        """
        try:
            accounts = Account.objects.filter(user__id=user_id)
            if not accounts:
                raise status.HTTP_404_NOT_FOUND(
                    "No Accounts found for the given user_id."
                )
            payments = Payment.objects.filter(
                account_id__in=accounts
            ).select_related(
                "user_subscription__service_id",
                "account_id",
                "cashback_applied",
            )
            payments_data = PaymentsSerializer(payments, many=True).data
            return Response(payments_data, status=status.HTTP_200_OK)
        except Account.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class ServicePaymentsView(APIView):  # ГОТОВО (два запроса в бд)
    def get(self, request, user_id: int, service_id: int) -> Response:
        """
        Метод получения данных о платежах для указанного пользователя
        по указанному идентификатору сервиса.

        Параметры:
            user_id: идентификатор пользователя
            service_id: идентификатор сервиса

        Возвращает:
            Данные о платежах с указанным статусом ответа.
        """
        try:
            accounts = Account.objects.filter(user__id=user_id)
            if not accounts:
                raise status.HTTP_404_NOT_FOUND(
                    "No Accounts found for the given user_id."
                )
            payments = (
                Payment.objects.filter(account_id__in=accounts)
                .select_related("user_subscription__service_id")
                .select_related("account_id")
                .select_related("cashback_applied")
            ).filter(user_subscription__service_id=service_id)
            payments_data = PaymentsSerializer(payments, many=True).data
            return Response(payments_data, status=status.HTTP_200_OK)
        except Account.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class AccountPaymentView(APIView):  # ГОТОВО (один запрос в бд)
    def get(self, request, account_id: int) -> Response:
        """
        Метод получения данных о платежах для указанного аккаунта.

        Параметры:
            account_id: идентификатор аккаунта

        Возвращает:
            Данные о платежах по указанному аккаунту.
        """
        try:
            payments = (
                Payment.objects.filter(account_id=account_id)
                .select_related("user_subscription__service_id")
                .select_related("account_id")
                .select_related("cashback_applied")
            )
            payments_data = PaymentsSerializer(payments, many=True).data
            return Response(payments_data, status=status.HTTP_200_OK)
        except Account.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class AccountView(APIView):
    """
    Метод создания нового платежного счёта для указанного аккаунта.

    Параметры:
        account_id: идентификатор аккаунта
        account_status: статус привязки счёта

    Возвращает:
        Данные о новом платежном счёте для указанного аккаунта.
    """

    def post(self, request, account_id: int, account_status: str) -> Response:
        data = {
            "account_status": account_status,
        }
        serializer = AccountSerializer(data=data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(
        self,
        request,
        account_id: int,
        account_status: str,
    ) -> Response:
        """
        Метод изменения данных о платежах пользователя для указанного аккаунта.

        Параметры:
            account_id: идентификатор аккаунта
            account_status: статус привязки счёта

        Возвращает:
            Изменение данных о платеже пользователя для указанного аккаунта.
        """
        try:
            account_to_patch = Account.objects.get(
                user__id=request.user.id, id=account_id
            )
        except Account.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        data = {"account_status": account_status}
        serializer = AccountSerializer(
            account_to_patch, data=data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_200_OK)


class PaymentsPeriodView(APIView):  # ГОТОВО (один запрос в бд)
    def get(self, request, user_id: int, time_period: str) -> Response:
        """
        Метод получения данных о платежах для указанного пользователя
        по указанному периоду времени.

        Параметры:
            user_id: идентификатор пользователя
            time_period: 2022-01-01_2022-01-31
            (дата начала_дата конца)

        Возвращает:
            Данные о платежах с указанным статусом ответа.
        """
        try:
            start_date_str, end_date_str = time_period.split("_")
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d")

            accounts = Account.objects.filter(user__id=user_id)
            if not accounts:
                raise status.HTTP_404_NOT_FOUND(
                    "No Accounts found for the given user_id."
                )
            payments = (
                Payment.objects.filter(
                    Q(account_id__in=accounts)
                    & Q(date__range=(start_date, end_date))
                )
                .select_related("user_subscription__service_id")
                .select_related("account_id")
                .select_related("cashback_applied")
            )
            payments_data = PaymentsSerializer(payments, many=True).data
            return Response(payments_data, status=status.HTTP_200_OK)
        except Account.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


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
        except Subscription.DoesNotExist:
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


class DocumentView(APIView):  # ГОТОВО (один запрос в бд)
    def get(self, request):
        """
        Метод получения данных правил сервиса.

        Возвращает:
            Данные о платежах с указанным статусом ответа.
        """
        try:
            document = Document.objects.latest("id")
        except Document.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        document_data = DocumentSerializer(document).data
        return Response(document_data, status=status.HTTP_200_OK)


class PaymentView(APIView):  # ГОТОВО (один запрос в бд)
    def get(self, request, payment_id):
        """
        Метод получения данных о конкретном платеже.

        Параметры:
            payment_id: идентификатор платежа

        Возвращает:
            Данные о платеже с указанным статусом ответа.
        """
        try:
            payment = (
                Payment.objects.filter(id=payment_id)
                .select_related("user_subscription__service_id")
                .select_related("account_id")
                .select_related("cashback_applied")
                .first()
            )
            payment_data = PaymentsSerializer(payment).data
            return Response(payment_data, status=status.HTTP_200_OK)
        except Payment.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class AvailableServicesView(APIView):
    def get(self, request):
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


class СategoriesView(APIView):
    def get(self, request, category_name: str):
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
