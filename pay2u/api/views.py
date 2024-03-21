from datetime import datetime

from django.db.models import Q
from payments.models import Document, Payment
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from subscriptions.models import UserSubscription
from users.models import Account

from .serializers import (
    DocumentSerializer,
    MainPageSerializer,
    PaymentsSerializer,
)


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
    def get(self, request, user_id):
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
    def get(self, request, user_id, service_id):
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
    def get(self, request, account_id):
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


class PaymentsPeriodView(APIView):  # ГОТОВО (один запрос в бд)
    def get(self, request, user_id, time_period):
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


class PaymentView(APIView):
    def get(self, request, payment_id):
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
