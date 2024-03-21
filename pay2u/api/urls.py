from django.urls import path

from .views import (
    MainPageView,
    PaymentsView,
    ServicePaymentsView,
    AccountPaymentView,
    PaymentsPeriodView,
    DocumentView,
)

urlpatterns = [
    path(
        "v1/users/<int:user_id>/main_page/",
        MainPageView.as_view(),
        name="main_page",
    ),
    path(
        "v1/users/<int:user_id>/payments/",
        PaymentsView.as_view(),
        name="payments",
    ),
    path(
        "v1/users/<int:user_id>/services/<service_id>/payment_history/",
        ServicePaymentsView.as_view(),
        name="service_payments",
    ),
    path(
        "v1/accounts/<int:account_id>/payment_history/",
        AccountPaymentView.as_view(),
        name="account_payments",
    ),
    path(
        "v1/users/<int:user_id>/payment_history/<str:time_period>/",
        PaymentsPeriodView.as_view(),
        name="payments_period",
    ),
    path(
        "v1/rules/", DocumentView.as_view(), name="rules"
    )
]
