from rest_framework import viewsets
from rest_framework.response import Response

from api.serializers import UserSerializer
from users.models import User


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()

    def list(self, request):
        serializer = UserSerializer(self.queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request):
        """
        A simple ViewSet for listing or retrieving user credentials.
        """
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
