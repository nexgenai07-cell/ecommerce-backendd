# PATH: ecommerce/apps/notifications/models.py
# NOTE: This replaces the original models8 file.
#       Changes from original:
#       - Added store ForeignKey
#       - Added sent_via field
#       - Expanded TYPE_CHOICES to match project requirements

from django.db import models
from django.conf import settings


class Notification(models.Model):
    """
    Stores all notifications sent to users.
    Covers order updates, payment alerts, system messages, and low stock alerts.
    sent_via tracks the delivery channel — whatsapp, email, or web.
    """

    TYPE_CHOICES = [
        ('order_confirm',   'Order Confirmed'),
        ('order_shipped',   'Order Shipped'),
        ('order_delivered', 'Order Delivered'),
        ('order_cancelled', 'Order Cancelled'),
        ('low_stock',       'Low Stock Alert'),
        ('payment',         'Payment Update'),
        ('system',          'System'),
        ('general',         'General'),
    ]

    SENT_VIA_CHOICES = [
        ('whatsapp', 'WhatsApp'),
        ('email',    'Email'),
        ('web',      'Web'),
    ]

    store      = models.ForeignKey(
                   'stores.Store',
                   on_delete=models.CASCADE,
                   related_name='notifications',
                 )
    user       = models.ForeignKey(
                   settings.AUTH_USER_MODEL,
                   on_delete=models.CASCADE,
                   related_name='notifications',
                   null=True,
                   blank=True,
                   help_text='Null for broadcast notifications'
                 )
    title      = models.CharField(max_length=255)
    message    = models.TextField()
    type       = models.CharField(max_length=20, choices=TYPE_CHOICES, default='general')
    is_read    = models.BooleanField(default=False)
    sent_via   = models.CharField(
                   max_length=20,
                   choices=SENT_VIA_CHOICES,
                   default='web',
                 )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.title} → {self.user.email if self.user else "broadcast"}'
