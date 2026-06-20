# PATH: apps/cart/wishlist_serializers.py

from rest_framework import serializers
from .models import Wishlist, WishlistItem
from apps.products.models import Product


class WishlistItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_price = serializers.DecimalField(source='product.price', max_digits=10, decimal_places=2, read_only=True)
    product_image = serializers.SerializerMethodField()
    product_in_stock = serializers.BooleanField(source='product.in_stock', read_only=True)

    class Meta:
        model = WishlistItem
        fields = ['id', 'product', 'product_name', 'product_price', 'product_image', 'product_in_stock', 'created_at']

    def get_product_image(self, obj):
        img = obj.product.primary_image
        return img.image_url if img else None


class WishlistSerializer(serializers.ModelSerializer):
    items = WishlistItemSerializer(many=True, read_only=True)

    class Meta:
        model = Wishlist
        fields = ['id', 'items', 'created_at']


class AddToWishlistSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()

    def validate_product_id(self, value):
        if not Product.objects.filter(id=value, is_active=True).exists():
            raise serializers.ValidationError('Product not found.')
        return value