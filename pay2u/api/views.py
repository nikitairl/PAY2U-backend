from datetime import datetime

from django.db.models import Q
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from payments.models import Payment
from subscriptions.models import UserSubscription
from users.models import Account
from .serializers import AccountSerializer, MainPageSerializer, PaymentsSerializer


class MainPageView(APIView):  # ДОДЕЛАТЬ (один запрос в бд)
    def get(self, user_id: int) -> Response:
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
    def get(self, user_id: int) -> Response:
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
    def get(self, user_id: int, service_id: int) -> Response:
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
    def get(self, account_id: int) -> Response:
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
    def patch(
            self,
            request,
            account_id: int,
            account_status: str,
    ) -> Response:
        """
        Метод изменения данных о платежах пользователя для указанного аккаунта.

        Параметры:
            user_id: идентификатор пользователя
            account_id: идентификатор аккаунта
            account_status: статус привязки счёта

        Возвращает:
            Изменение данных о платеже пользователя для указанного аккаунта.
        """
        try:
            account_to_patch = (
                Account.objects.get(user__id=request.user.id, id=account_id)
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
            print(payments)
            payments_data = PaymentsSerializer(payments, many=True).data
            return Response(payments_data, status=status.HTTP_200_OK)
        except Account.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
