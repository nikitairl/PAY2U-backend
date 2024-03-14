from django.contrib.auth.models import User
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

# from .serializers import UserSerializer


# class UserSelfViewSet(viewsets.ReadOnlyModelViewSet):
#     serializer_class = UserSerializer
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         # Filter the queryset to only include the current user
#         user = self.request.user
#         return User.objects.filter(pk=user.pk)

#     def list(self, request, *args, **kwargs):
#         # Redirect the list action to retrieve, to return the current user
#         return self.retrieve(request, *args, **kwargs)
