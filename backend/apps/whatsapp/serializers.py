# PATH: apps/whatsapp/serializers.py

from rest_framework import serializers
from .models import WhatsAppLog, WhatsAppSession


class WhatsAppLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = WhatsAppLog
        fields = ['id', 'phone_number', 'direction', 'message', 'is_admin', 'metadata', 'created_at']


class WhatsAppSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = WhatsAppSession
        fields = ['id', 'phone_number', 'is_admin', 'current_flow', 'state_data', 'last_active', 'created_at']


class SendWhatsAppMessageSerializer(serializers.Serializer):
    """POST /api/v1/whatsapp/send/ — body shape"""
    phone_number = serializers.CharField()
    message = serializers.CharField()