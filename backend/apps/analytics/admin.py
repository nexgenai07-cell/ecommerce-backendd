# PATH: apps/analytics/admin.py

from django.contrib import admin
from .models import CustomerBehavior


@admin.register(CustomerBehavior)
class CustomerBehaviorAdmin(admin.ModelAdmin):
    # Useful for admin to quickly see what action happened on which entity
    list_display = ['id', 'user', 'session_key', 'action', 'entity_type', 'entity_id', 'created_at']
    list_filter = ['action', 'entity_type']
    search_fields = ['session_key', 'user__email']
