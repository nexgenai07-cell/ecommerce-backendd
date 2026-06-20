# PATH: apps/stores/views.py

from rest_framework import generics, permissions
from .models import Store
from .serializers import StoreSerializer
from apps.users.permissions import IsAdmin


class MyStoreView(generics.RetrieveUpdateAPIView):
    """
    GET /api/v1/stores/me/  -> view current store details (any authenticated user)
    PUT /api/v1/stores/me/  -> update store details (admin only)

    Single-store setup — always returns the one store that exists.
    """
    serializer_class = StoreSerializer

    def get_object(self):
        return Store.objects.first()

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated(), IsAdmin()]