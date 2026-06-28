# PATH: apps/notifications/admin.py

from django.contrib import admin
from .models import Notification


# Registering Notification model so admin can view/manage notifications
# directly from the Django admin panel (useful for debugging delivery issues)
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    # Columns shown in the admin list view
    list_display = ['id', 'title', 'type', 'sent_via', 'user', 'is_read', 'created_at']
    # Sidebar filters — quick way to find e.g. all unread WhatsApp notifications
    list_filter = ['type', 'sent_via', 'is_read']
    # Search bar — search by title or message text
    search_fields = ['title', 'message']
