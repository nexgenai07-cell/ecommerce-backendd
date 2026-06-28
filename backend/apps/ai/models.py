# PATH: ecommerce/apps/ai/models.py

from django.db import models
from django.conf import settings


class ChatSession(models.Model):
    """
    Tracks a conversation session between a user and the AI assistant.
    Anonymous users get a session_key (stored in cookie/localStorage).
    Registered users are linked via ForeignKey.
    On login, anonymous session is merged with the user's account.
    """

    user        = models.ForeignKey(
                    settings.AUTH_USER_MODEL,
                    on_delete=models.CASCADE,
                    related_name='chat_sessions',
                    null=True,
                    blank=True,
                  )
    store       = models.ForeignKey(
                    'stores.Store',
                    on_delete=models.CASCADE,
                    related_name='chat_sessions',
                  )
    session_key = models.CharField(max_length=100, unique=True)
    started_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'chat_sessions'
        ordering = ['-started_at']

    def __str__(self):
        if self.user:
            return f'Session {self.session_key} ({self.user.email})'
        return f'Session {self.session_key} (anonymous)'


class ChatMessage(models.Model):
    """
    Stores individual messages within a chat session.
    metadata field stores structured data like product lists,
    order info, cart state returned by AI tools.
    """

    SENDER_CHOICES = [
        ('user', 'User'),
        ('ai',   'AI'),
    ]

    session    = models.ForeignKey(
                   ChatSession,
                   on_delete=models.CASCADE,
                   related_name='messages',
                 )
    sender     = models.CharField(max_length=10, choices=SENDER_CHOICES)
    message    = models.TextField()
    metadata   = models.JSONField(
                   null=True,
                   blank=True,
                   help_text='Structured data: product cards, order info, cart state etc.'
                 )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'chat_messages'
        ordering = ['created_at']

    # PATH: ecommerce/apps/ai/models.py  (add below ChatMessage)
# OR create a separate: ecommerce/apps/stores/models.py (append)
# Recommended: keep in ecommerce/apps/ai/models.py alongside ChatSession

from django.db import models
from django.conf import settings


class AuditLog(models.Model):
    """
    Records every admin action taken through the WhatsApp bot or admin panel.
    Required for compliance and accountability in a real client project.
    old_data and new_data store JSON snapshots of the record before and after change.
    """

    store      = models.ForeignKey(
                   'stores.Store',
                   on_delete=models.CASCADE,
                   related_name='audit_logs',
                 )
    user       = models.ForeignKey(
                   settings.AUTH_USER_MODEL,
                   on_delete=models.SET_NULL,
                   related_name='audit_logs',
                   null=True,
                   blank=True,
                   help_text='Admin who performed the action'
                 )
    action     = models.CharField(
                   max_length=100,
                   help_text='e.g. create_product, update_order_status, delete_category'
                 )
    entity     = models.CharField(
                   max_length=50,
                   help_text='e.g. product, order, category, inventory'
                 )
    entity_id  = models.IntegerField(
                   null=True,
                   blank=True,
                   help_text='ID of the affected record'
                 )
    old_data   = models.JSONField(
                   null=True,
                   blank=True,
                   help_text='Snapshot of record BEFORE the change'
                 )
    new_data   = models.JSONField(
                   null=True,
                   blank=True,
                   help_text='Snapshot of record AFTER the change'
                 )
    ip_address = models.CharField(
                   max_length=50,
                   null=True,
                   blank=True,
                   help_text='IP address of the request — null for WhatsApp actions'
                 )
    source     = models.CharField(
                   max_length=20,
                   default='web',
                   help_text='Where the action came from: web, whatsapp'
                 )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'audit_logs'
        ordering = ['-created_at']
        indexes  = [
            models.Index(fields=['store', 'entity', 'created_at']),
            models.Index(fields=['user', 'created_at']),
        ]

    def __str__(self):
        actor = self.user.email if self.user else 'system'
        return f'{actor} → {self.action} on {self.entity}:{self.entity_id}'


    def __str__(self):
        return f'[{self.sender}] {self.message[:50]}'
