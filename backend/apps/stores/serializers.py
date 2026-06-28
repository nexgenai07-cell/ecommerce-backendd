# PATH: apps/stores/serializers.py

from rest_framework import serializers
from .models import Store


class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = [
            'id', 'name', 'logo', 'subdomain', 'phone', 'address',
            'plan', 'is_active', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'subdomain', 'plan', 'created_at', 'updated_at']