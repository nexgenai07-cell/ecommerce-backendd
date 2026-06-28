# PATH: apps/returns/serializers.py

from rest_framework import serializers
from .models import Return


class ReturnSerializer(serializers.ModelSerializer):
    order_number = serializers.CharField(source='order.order_number', read_only=True)
    customer_name = serializers.CharField(source='customer.name', read_only=True)

    class Meta:
        model = Return
        fields = ['id', 'order', 'order_number', 'customer', 'customer_name', 'reason', 'status', 'resolved_at', 'created_at']
        read_only_fields = ['id', 'status', 'resolved_at', 'created_at']


class CreateReturnSerializer(serializers.Serializer):
    reason = serializers.CharField()


class AdminReturnStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=['approved', 'rejected'])