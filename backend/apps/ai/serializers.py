# PATH: apps/ai/serializers.py

from rest_framework import serializers
from .models import ChatSession, ChatMessage, AuditLog


class ChatMessageSerializer(serializers.ModelSerializer):
    """Used to show individual messages inside a chat session's history."""

    class Meta:
        model = ChatMessage
        fields = ['id', 'sender', 'message', 'metadata', 'created_at']
        # id and created_at are set automatically, never sent by the client
        read_only_fields = ['id', 'created_at']


class ChatSessionSerializer(serializers.ModelSerializer):
    """Lightweight serializer — used when listing sessions, no messages included."""

    class Meta:
        model = ChatSession
        fields = ['id', 'session_key', 'user', 'store', 'started_at', 'updated_at']
        read_only_fields = ['id', 'started_at', 'updated_at']


class ChatSessionHistorySerializer(serializers.ModelSerializer):
    """Full serializer — used for the 'history' endpoint, includes all messages."""

    # nested messages, ordered oldest -> newest (handled by Meta.ordering on ChatMessage)
    messages = ChatMessageSerializer(many=True, read_only=True)

    class Meta:
        model = ChatSession
        fields = ['id', 'session_key', 'user', 'store', 'started_at', 'updated_at', 'messages']


class AuditLogSerializer(serializers.ModelSerializer):
    """Read-only serializer — audit logs are created by the system, not via API input."""

    # shows the admin's email instead of just their numeric id, easier to read
    user_email = serializers.CharField(source='user.email', read_only=True, default='system')

    class Meta:
        model = AuditLog
        fields = [
            'id', 'user', 'user_email', 'action', 'entity', 'entity_id',
            'old_data', 'new_data', 'ip_address', 'source', 'created_at',
        ]
        read_only_fields = fields  # nothing on AuditLog should be editable through the API
