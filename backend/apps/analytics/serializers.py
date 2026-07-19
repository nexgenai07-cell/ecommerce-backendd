# PATH: apps/analytics/serializers.py

from rest_framework import serializers
from .models import CustomerBehavior


class CustomerBehaviorSerializer(serializers.ModelSerializer):
    """
    Used both for:
    - tracking a new action (POST) — e.g. when customer views a product
    - listing behavior records for admin analytics (GET)
    """

    class Meta:
        model = CustomerBehavior
        fields = [
            'id', 'user', 'session_key', 'action',
            'entity_type', 'entity_id', 'metadata', 'created_at',
        ]
        # user and store are set automatically from the request, not from client input
        read_only_fields = ['id', 'user', 'created_at']