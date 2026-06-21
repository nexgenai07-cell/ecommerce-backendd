# PATH: apps/whatsapp/admin.py

from django.contrib import admin
from .models import WhatsAppLog, WhatsAppSession


@admin.register(WhatsAppLog)
class WhatsAppLogAdmin(admin.ModelAdmin):
    list_display = ['id', 'phone_number', 'direction', 'is_admin', 'created_at']
    list_filter = ['direction', 'is_admin']
    search_fields = ['phone_number', 'message']


@admin.register(WhatsAppSession)
class WhatsAppSessionAdmin(admin.ModelAdmin):
    list_display = ['id', 'phone_number', 'is_admin', 'current_flow', 'last_active']
    search_fields = ['phone_number']