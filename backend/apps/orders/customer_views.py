# PATH: apps/orders/customer_views.py

from rest_framework import generics, permissions
from django.db.models import Q
from .models import Customer
from .customer_serializers import CustomerAdminSerializer
from apps.users.permissions import IsAdmin

# Returns a searchable list of all customers for administrators.
class AdminCustomerListView(generics.ListAPIView):
    """
    GET /api/v1/admin/customers/?search=
    Admin-only — list all customers with order count and total spent.
    """
    serializer_class = CustomerAdminSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]
    
# Fetches all customers and applies search filters if provided.
    def get_queryset(self):
        qs = Customer.objects.select_related('user').all().order_by('-created_at')
        search = self.request.query_params.get('search')
        if search:
            qs = qs.filter(Q(name__icontains=search) | Q(phone__icontains=search) | Q(email__icontains=search))
        return qs

# Returns complete information for a selected customer.
class AdminCustomerDetailView(generics.RetrieveAPIView):
    """GET /api/v1/admin/customers/{id}/"""
    serializer_class = CustomerAdminSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]
    queryset = Customer.objects.select_related('user').all()