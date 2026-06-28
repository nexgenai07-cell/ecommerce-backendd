# PATH: ecommerce/apps/social/models.py

from django.db import models
from django.conf import settings


class SocialAccount(models.Model):
    """
    Stores connected Instagram and Facebook accounts for a store.
    Access tokens are stored encrypted (encryption handled at service layer).
    One store can have one Instagram and one Facebook account connected.
    """

    PLATFORM_CHOICES = [
        ('instagram', 'Instagram'),
        ('facebook',  'Facebook'),
    ]

    store        = models.ForeignKey(
                     'stores.Store',
                     on_delete=models.CASCADE,
                     related_name='social_accounts',
                   )
    platform     = models.CharField(max_length=20, choices=PLATFORM_CHOICES)
    account_name = models.CharField(max_length=200)
    access_token = models.TextField(
                     help_text='Encrypted access token — never store plain text'
                   )
    token_expiry = models.DateTimeField(
                     null=True,
                     blank=True,
                     help_text='When the access token expires — used for renewal alerts'
                   )
    page_id      = models.CharField(
                     max_length=200,
                     null=True,
                     blank=True,
                     help_text='Facebook Page ID or Instagram Business Account ID'
                   )
    is_active    = models.BooleanField(default=True)
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    class Meta:
        db_table        = 'social_accounts'
        unique_together = ['store', 'platform']

    def __str__(self):
        return f'{self.store.name} — {self.platform} ({self.account_name})'


class SocialPost(models.Model):
    """
    Represents a social media post — auto-generated or manually created.
    Lifecycle: draft → pending → approved → scheduled → published
                                          → rejected
                                                      → failed (retry possible)
    AI generates caption + hashtags when a new product is added.
    Admin approves via WhatsApp before publishing.
    """

    STATUS_CHOICES = [
        ('draft',     'Draft'),
        ('pending',   'Pending Approval'),
        ('approved',  'Approved'),
        ('scheduled', 'Scheduled'),
        ('published', 'Published'),
        ('failed',    'Failed'),
        ('rejected',  'Rejected'),
    ]

    PLATFORM_CHOICES = [
        ('instagram', 'Instagram'),
        ('facebook',  'Facebook'),
        ('both',      'Both'),
    ]

    store        = models.ForeignKey(
                     'stores.Store',
                     on_delete=models.CASCADE,
                     related_name='social_posts',
                   )
    product      = models.ForeignKey(
                     'products.Product',
                     on_delete=models.SET_NULL,
                     related_name='social_posts',
                     null=True,
                     blank=True,
                     help_text='Product this post is about — null for manual posts'
                   )
    platform     = models.CharField(max_length=20, choices=PLATFORM_CHOICES)
    caption      = models.TextField()
    hashtags     = models.TextField(
                     help_text='Space-separated hashtags e.g. #Samsung #GalaxyS25'
                   )
    image_url    = models.CharField(max_length=500)
    status       = models.CharField(
                     max_length=20,
                     choices=STATUS_CHOICES,
                     default='draft',
                   )
    scheduled_at = models.DateTimeField(
                     null=True,
                     blank=True,
                     help_text='When to publish — set after admin approval'
                   )
    published_at = models.DateTimeField(
                     null=True,
                     blank=True,
                     help_text='Actual time of successful publish'
                   )
    ig_post_id   = models.CharField(
                     max_length=200,
                     null=True,
                     blank=True,
                     help_text='Instagram post ID after successful publish'
                   )
    fb_post_id   = models.CharField(
                     max_length=200,
                     null=True,
                     blank=True,
                     help_text='Facebook post ID after successful publish'
                   )
    created_by   = models.ForeignKey(
                     settings.AUTH_USER_MODEL,
                     on_delete=models.SET_NULL,
                     null=True,
                     blank=True,
                     related_name='social_posts',
                     help_text='Admin who created/approved this post'
                   )
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'social_posts'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.platform} post [{self.status}] — {self.created_at.date()}'


class SocialPostAnalytics(models.Model):
    """
    Stores engagement metrics for published social posts.
    Updated daily via Celery Beat task that fetches from Instagram/Facebook APIs.
    """

    post      = models.OneToOneField(
                  SocialPost,
                  on_delete=models.CASCADE,
                  related_name='analytics',
                )
    likes     = models.IntegerField(default=0)
    comments  = models.IntegerField(default=0)
    shares    = models.IntegerField(default=0)
    reach     = models.IntegerField(
                  default=0,
                  help_text='Number of unique accounts that saw this post'
                )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'social_post_analytics'

    def __str__(self):
        return f'Analytics for post {self.post.id}'
