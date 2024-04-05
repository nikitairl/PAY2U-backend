from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Account
from .serializers import AccountSerializer


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
