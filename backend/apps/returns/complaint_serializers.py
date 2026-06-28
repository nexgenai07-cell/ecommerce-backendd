# PATH: apps/returns/complaint_serializers.py
# (Complaint model lives in apps/returns alongside Return — see models_returns_updated.py)

from rest_framework import serializers
from .models import Complaint


class ComplaintSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.name', read_only=True)
    order_number = serializers.CharField(source='order.order_number', read_only=True, default=None)
    resolved_by_name = serializers.CharField(source='resolved_by.name', read_only=True, default=None)

    class Meta:
        model = Complaint
        fields = [
            'id', 'customer', 'customer_name', 'order', 'order_number',
            'message', 'type', 'status', 'response', 'resolved_by_name', 'created_at',
        ]
        read_only_fields = ['id', 'status', 'response', 'created_at']


class CreateComplaintSerializer(serializers.Serializer):
    TYPE_CHOICES = ['order', 'payment', 'product', 'delivery', 'other']

    type = serializers.ChoiceField(choices=TYPE_CHOICES)
    order = serializers.IntegerField(required=False, allow_null=True)
    message = serializers.CharField()


class AdminComplaintStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=['open', 'in_progress', 'resolved', 'closed'])


class AdminComplaintRespondSerializer(serializers.Serializer):
    response = serializers.CharField()