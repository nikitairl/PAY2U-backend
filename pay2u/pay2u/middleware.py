from django.contrib.auth import get_user_model, login
from django.contrib.auth.backends import ModelBackend


class AutoLoginMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.user.is_authenticated:
            default_phone = "7999999999"
            default_email = "default@example.com"
            password = "a"
            User = get_user_model()
            try:
                user = User.objects.get(phone=default_phone)
            except User.DoesNotExist:
                # Создает пользователя если такого нет
                user = User.objects.create_superuser(
                    phone=default_phone,
                    email=default_email,
                    password=password,
                )
                user.save()

            # Авторизует деф пользователя
            backend = ModelBackend()
            user.backend = f"{backend.__module__}.{backend.__class__.__name__}"
            login(request, user)

        response = self.get_response(request)
        return response
