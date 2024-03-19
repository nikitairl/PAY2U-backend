from payments.models import Payment
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from subscriptions.models import UserSubscription
from users.models import Account

from .serializers import MainPageSerializer, PaymentsSerializer


class MainPageView(APIView):
    def get(self, request, user_id):
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


class PaymentsView(APIView):
    def get(self, request, user_id):
        try:
            # Find the account(s) related to the user_id
            accounts = Account.objects.filter(user__id=user_id)
            if not accounts:
                raise status.HTTP_404_NOT_FOUND(
                    "No Accounts found for the given user_id."
                )

            # Get all payments for the user's account(s)
            payments = Payment.objects.filter(
                account_id__in=accounts
            ).select_related("user_subscription__service_id")
            payments_data = PaymentsSerializer(payments, many=True).data
            return Response(payments_data, status=status.HTTP_200_OK)
        except Account.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
