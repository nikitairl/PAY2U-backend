from django.urls import path

from .views import UserViewSet

urlpatterns = [
    path("v1/users/", UserViewSet.as_view({"get": "list"})),
    path("v1/users/self/", UserViewSet.as_view({"get": "retrieve"})),
]
