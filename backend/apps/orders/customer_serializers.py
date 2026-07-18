# PATH: apps/orders/customer_serializers.py

from rest_framework import serializers
from .models import Customer

# Converts customer information into API response for the admin panel.
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

# Counts the total number of orders placed by the customer.
    def get_total_orders(self, obj):
        return obj.orders.count()

# Calculates the customer's total spending, excluding cancelled orders.
    def get_total_spent(self, obj):
        return sum(o.total_amount for o in obj.orders.exclude(status='cancelled'))