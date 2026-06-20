# PATH: apps/social/serializers.py

from rest_framework import serializers
from .models import SocialAccount, SocialPost, SocialPostAnalytics


class SocialAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialAccount
        fields = [
            'id', 'platform', 'account_name', 'token_expiry',
            'page_id', 'is_active', 'created_at',
        ]
        # access_token is intentionally excluded — never sent back to the client
        read_only_fields = ['id', 'created_at']


class SocialPostAnalyticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialPostAnalytics
        fields = ['likes', 'comments', 'shares', 'reach', 'updated_at']
        read_only_fields = fields  # analytics are fetched from Instagram/Facebook, not edited manually


class SocialPostSerializer(serializers.ModelSerializer):
    """Full serializer — used for listing and detail view, includes analytics if available."""

    # nested, read-only — will be null until the post is published and analytics are fetched
    analytics = SocialPostAnalyticsSerializer(read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True, default=None)

    class Meta:
        model = SocialPost
        fields = [
            'id', 'product', 'product_name', 'platform', 'caption', 'hashtags',
            'image_url', 'status', 'scheduled_at', 'published_at',
            'ig_post_id', 'fb_post_id', 'created_by', 'analytics', 'created_at',
        ]
        # status/published fields are controlled by the approval workflow, not free text edits
        read_only_fields = [
            'id', 'status', 'published_at', 'ig_post_id', 'fb_post_id',
            'created_by', 'created_at',
        ]


class SocialPostCreateSerializer(serializers.ModelSerializer):
    """Used when admin manually creates a post (not AI-generated)."""

    class Meta:
        model = SocialPost
        fields = ['id', 'product', 'platform', 'caption', 'hashtags', 'image_url', 'scheduled_at']
        read_only_fields = ['id']

    def create(self, validated_data):
        # Single-store setup — always attach the one store that exists.
        from apps.stores.models import Store
        request = self.context['request']
        validated_data['store'] = Store.objects.first()
        validated_data['created_by'] = request.user
        return super().create(validated_data)
