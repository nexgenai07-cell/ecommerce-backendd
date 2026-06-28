# PATH: ecommerce/apps/analytics/models.py

from django.db import models
from django.conf import settings


class CustomerBehavior(models.Model):
    """
    Tracks every meaningful action a customer takes on the platform.
    Used for analytics, recommendations, and AI personalization.
    Anonymous users are tracked via session_key.
    Registered users are tracked via user ForeignKey.
    """

    ACTION_CHOICES = [
        ('view',     'Product Viewed'),
        ('search',   'Product Searched'),
        ('cart_add', 'Added to Cart'),
        ('wishlist', 'Added to Wishlist'),
        ('purchase', 'Purchased'),
    ]

    store       = models.ForeignKey(
                    'stores.Store',
                    on_delete=models.CASCADE,
                    related_name='customer_behaviors',
                  )
    user        = models.ForeignKey(
                    settings.AUTH_USER_MODEL,
                    on_delete=models.SET_NULL,
                    related_name='behaviors',
                    null=True,
                    blank=True,
                  )
    session_key = models.CharField(
                    max_length=100,
                    null=True,
                    blank=True,
                    help_text='For anonymous users — linked to ChatSession.session_key'
                  )
    action      = models.CharField(max_length=20, choices=ACTION_CHOICES)
    entity_type = models.CharField(
                    max_length=50,
                    help_text='e.g. product, category, search_query'
                  )
    entity_id   = models.IntegerField(
                    null=True,
                    blank=True,
                    help_text='ID of the entity (product_id, category_id etc.)'
                  )
    metadata    = models.JSONField(
                    null=True,
                    blank=True,
                    help_text='Extra context: search query text, price filter, etc.'
                  )
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'customer_behavior'
        ordering = ['-created_at']
        indexes  = [
            models.Index(fields=['store', 'action', 'created_at']),
            models.Index(fields=['user', 'action']),
            models.Index(fields=['session_key']),
        ]

    def __str__(self):
        actor = self.user.email if self.user else f'anon:{self.session_key}'
        return f'{actor} → {self.action} on {self.entity_type}:{self.entity_id}'
