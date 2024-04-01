from datetime import datetime, timedelta

from django.db.models import Q, Min
from django.middleware.csrf import get_token
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from payments.models import Payment, Document
from services.models import Service
from subscriptions.models import UserSubscription, Subscription
from users.models import Account, User
from .serializers import (
    AccountSerializer,
    AvailableServiceSerializer,
    DocumentSerializer,
    MainPageSerializer,
    PaymentsSerializer,
    UserPaymentsPlanSerializer,
    UserSubscriptionSerializer,
    UserSubscriptionsSerializer
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
        except UserSubscription.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        subscription_data = UserSubscriptionSerializer(user_subscription).data
        return Response(subscription_data, status=status.HTTP_200_OK)


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


class СategoriesView(APIView):
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
    def post(self, request, user_id: int):
        """
        Метод организации подписок для пользователя.
        Если подписка уже есть - продлевает.
        Если подписка уже есть, но другой тариф - заменяет.
        Если подписки нет - создает новую.
        post request example:
                                {
                                    "subscription_id": "3",
                                    "account_id": "1",
                                    "user_email": "example@example.ru"
                                }
        Параметры:
            user_id (int): идентификатор пользователя

        Returns:
            Сообщение с кодом + описанием ошибки или созданную подписку.
        """
        user = get_object_or_404(User, id=user_id)
        new_subscription_id = request.data.get("subscription_id")
        subscription = Subscription.objects.get(id=new_subscription_id)
        account_id = request.data.get("account_id")

        account_balance = get_object_or_404(Account, id=account_id)
        update_balance = self.update_balance(subscription, account_balance)
        if update_balance.balance < 0:
            data = {"error": "Недостаточно средств на счете."}
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
        # Проверка есть ли подписка на сервис
        service = subscription.service_id
        active_subscription = self.get_active_subscription(user.id, service)
        if active_subscription is not None:
            # Была ли именно эта подписка
            subscription_id = active_subscription.subscription.id
            if subscription_id == int(new_subscription_id):
                # Меняем статус на True, если она не была активна и ставим дату
                if active_subscription.status is False:
                    active_subscription.end = datetime.now()
                    active_subscription.status = True
                # Если была активна - не меняем дату и статус, добавляем время
                active_subscription.end = active_subscription.end + timedelta(
                    days=active_subscription.subscription.period
                )
                update_balance.save()
                return self.send_response(active_subscription)
            else:
                # Если подписка была, но другая - меняем статус и ставим дату
                self.deactivate_subscription(active_subscription)
        # Оформляем новую подписку
        update_balance.save()
        new_subscription = self.create_new_subscription(user, subscription)
        return self.send_response(new_subscription)

    def get_active_subscription(self, user_id, service):
        """
        Метод проверки подписки на сервис
        """
        try:
            return UserSubscription.objects.get(
                user_id=user_id,
                subscription__service_id=service,
                status=True
            )
        except UserSubscription.DoesNotExist:
            return None

    def deactivate_subscription(self, subscription):
        """
        Метод деактивации подписки
        """
        subscription.end = datetime.now()
        subscription.status = False
        subscription.renewal = False
        subscription.save()

    def update_balance(self, subscription, account_balance):
        """
        Калькуляция баланса
        """
        account_balance.balance -= subscription.price
        return account_balance

    def create_new_subscription(self, user, subscription):
        """
        Создание нового объекта подписки
        """
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
        return new_subscription

    def send_response(self, subscription):
        ser_data = UserSubscriptionSerializer(subscription).data
        subscription.save()
        return Response(ser_data, status=status.HTTP_200_OK)
