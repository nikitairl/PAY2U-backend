from django.urls import path

from .views import MainPageView, PaymentsView

urlpatterns = [
    path(
        "v1/users/<int:user_id>/main_page",
        MainPageView.as_view(),
        name="main_page",
    ),
    path(
        "v1/users/<int:user_id>/payments",
        PaymentsView.as_view(),
        name="payments",
    ),
]
