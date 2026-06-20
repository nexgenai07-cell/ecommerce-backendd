# PATH: apps/categories/views.py

from rest_framework import viewsets, permissions
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from .models import Category
from .serializers import CategorySerializer
from apps.users.permissions import IsAdmin


class CategoryViewSet(viewsets.ModelViewSet):
    """
    GET    /api/v1/categories/       -> list (anyone)
    POST   /api/v1/categories/       -> create (admin only) — multipart, supports 'image' file
    GET    /api/v1/categories/{id}/  -> retrieve (anyone)
    PUT    /api/v1/categories/{id}/  -> update (admin only) — multipart, supports 'image' file
    DELETE /api/v1/categories/{id}/  -> delete (admin only)
    """
    serializer_class = CategorySerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        # Single store setup — in future multi-store, filter by request store
        return Category.objects.all().order_by('name')

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated(), IsAdmin()]