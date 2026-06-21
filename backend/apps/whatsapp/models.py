# PATH: apps/whatsapp/models.py

from django.db import models
from django.conf import settings


class WhatsAppLog(models.Model):
    """
    Every inbound and outbound WhatsApp message is recorded here.
    Used for: admin debugging, the "Bot conversation logs" admin page,
    and as an audit trail of what the bot said/did.
    """

    DIRECTION_CHOICES = [
        ('inbound', 'Inbound'),
        ('outbound', 'Outbound'),
    ]

    store        = models.ForeignKey('stores.Store', on_delete=models.CASCADE, related_name='whatsapp_logs')
    phone_number = models.CharField(max_length=20)
    direction    = models.CharField(max_length=10, choices=DIRECTION_CHOICES)
    message      = models.TextField()
    is_admin     = models.BooleanField(default=False, help_text='True if this number is a registered admin')
    metadata     = models.JSONField(null=True, blank=True, help_text='Raw payload, intent, tool calls etc.')
    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'whatsapp_logs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['phone_number', 'created_at']),
        ]

    def __str__(self):
        return f'[{self.direction}] {self.phone_number}: {self.message[:40]}'


class WhatsAppSession(models.Model):
    """
    Tracks multi-turn conversation state for a phone number — e.g. mid-way
    through "add product" flow (name collected, waiting for price).
    Mirrors what BE2's admin_agent.py will read/write from Redis at runtime;
    this DB table is the persistent/auditable record of session state.
    """

    phone_number  = models.CharField(max_length=20, unique=True)
    is_admin      = models.BooleanField(default=False)
    current_flow  = models.CharField(max_length=100, null=True, blank=True, help_text='e.g. add_product, checkout')
    state_data    = models.JSONField(null=True, blank=True, help_text='Collected fields so far in the current flow')
    last_active   = models.DateTimeField(auto_now=True)
    created_at    = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'whatsapp_sessions'

    def __str__(self):
        return f'{self.phone_number} ({self.current_flow or "idle"})'