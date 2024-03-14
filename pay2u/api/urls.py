from rest_framework.routers import DefaultRouter
from pay2u import users, subscriptions, services, payments, banking


router = DefaultRouter()
router.register(r"users", users.UserViewSet)
