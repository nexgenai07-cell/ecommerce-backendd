# PATH: apps/orders/customer_serializers.py

from rest_framework import serializers
from .models import Customer


class CustomerAdminSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True)
    total_orders = serializers.SerializerMethodField()
    total_spent = serializers.SerializerMethodField()

    class Meta:
        model = Customer
        fields = [
            'id', 'user', 'user_email', 'name', 'phone', 'email',
            'address', 'total_orders', 'total_spent', 'created_at',
        ]

    def get_total_orders(self, obj):
        return obj.orders.count()

    def get_total_spent(self, obj):
        return sum(o.total_amount for o in obj.orders.exclude(status='cancelled'))