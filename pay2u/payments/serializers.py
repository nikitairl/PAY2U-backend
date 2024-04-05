from rest_framework import serializers

from services.serializers import ServiceSerializer
from users.serializers import AccountSerializer
from .models import CashbackApplied, Document, Payment


class CashbackAppliedSerializer(serializers.ModelSerializer):
    class Meta:
        model = CashbackApplied
        fields = ("id", "amount", "applied_status")


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ("name", "text")


class PaymentsSerializer(serializers.ModelSerializer):
    service = ServiceSerializer(
        read_only=True, source="user_subscription.service_id"
    )
    account = AccountSerializer(read_only=True, source="account_id")
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
