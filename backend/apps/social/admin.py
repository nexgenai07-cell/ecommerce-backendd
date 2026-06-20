# PATH: apps/social/admin.py

from django.contrib import admin
from .models import SocialAccount, SocialPost, SocialPostAnalytics


@admin.register(SocialAccount)
class SocialAccountAdmin(admin.ModelAdmin):
    list_display = ['id', 'store', 'platform', 'account_name', 'is_active', 'token_expiry']
    list_filter = ['platform', 'is_active']
    # access_token is sensitive — never show it directly in the list view
    search_fields = ['account_name']


# Inline so analytics (likes, comments, shares) show inside the post's own admin page
class SocialPostAnalyticsInline(admin.StackedInline):
    model = SocialPostAnalytics
    extra = 0


@admin.register(SocialPost)
class SocialPostAdmin(admin.ModelAdmin):
    list_display = ['id', 'store', 'product', 'platform', 'status', 'scheduled_at', 'published_at']
    list_filter = ['platform', 'status']
    search_fields = ['caption', 'hashtags']
    inlines = [SocialPostAnalyticsInline]
