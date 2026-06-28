# PATH: apps/ai/admin.py

from django.contrib import admin
from .models import ChatSession, ChatMessage, AuditLog


# Inline so messages of a session can be viewed directly inside the
# ChatSession admin page, instead of opening a separate page
class ChatMessageInline(admin.TabularInline):
    model = ChatMessage
    extra = 0          # don't show empty extra rows
    readonly_fields = ['sender', 'message', 'metadata', 'created_at']
    can_delete = False  # chat history should not be deletable from admin


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ['id', 'session_key', 'user', 'store', 'started_at', 'updated_at']
    search_fields = ['session_key', 'user__email']
    list_filter = ['store']
    inlines = [ChatMessageInline]


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'session', 'sender', 'short_message', 'created_at']
    list_filter = ['sender']
    search_fields = ['message']

    # Shows a trimmed preview of the message in the list view (full text can be long)
    def short_message(self, obj):
        return obj.message[:50]
    short_message.short_description = 'Message'


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'action', 'entity', 'entity_id', 'source', 'created_at']
    list_filter = ['action', 'entity', 'source']
    search_fields = ['action', 'entity']
