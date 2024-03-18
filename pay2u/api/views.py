from rest_framework import viewsets
from rest_framework.response import Response

from api.serializers import UserSerializer
from users.models import User


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()

    def retrieve(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
