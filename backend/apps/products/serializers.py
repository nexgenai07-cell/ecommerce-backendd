# PATH: apps/products/serializers.py

from rest_framework import serializers
from .models import Product, ProductImage, ProductHistory


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'is_primary', 'created_at']


class ProductListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for product listing pages"""
    primary_image = serializers.SerializerMethodField()
    category_name = serializers.CharField(source='category.name', read_only=True, default=None)
    in_stock = serializers.BooleanField(read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'price', 'original_price', 'stock', 'in_stock',
            'sku', 'category', 'category_name', 'primary_image', 'is_active',
        ]

    def get_primary_image(self, obj):
        img = obj.primary_image
        if not img or not img.image:
            return None
        request = self.context.get('request')
        url = img.image.url
        return request.build_absolute_uri(url) if request else url


class ProductDetailSerializer(serializers.ModelSerializer):
    """Full serializer for single product page — includes all images"""
    images = ProductImageSerializer(many=True, read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True, default=None)
    in_stock = serializers.BooleanField(read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'price', 'original_price',
            'stock', 'in_stock', 'sku', 'category', 'category_name',
            'is_active', 'low_stock_threshold', 'publish_at',
            'images', 'created_at', 'updated_at',
        ]


class ProductCreateUpdateSerializer(serializers.ModelSerializer):
    """Used for admin POST/PUT — store is injected, not taken from client"""

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'price', 'original_price',
            'stock', 'sku', 'category', 'is_active',
            'low_stock_threshold', 'publish_at',
        ]
        read_only_fields = ['id']

    def validate_sku(self, value):
        qs = Product.objects.filter(sku=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError('A product with this SKU already exists.')
        return value

    def create(self, validated_data):
        request = self.context['request']
        validated_data['store'] = request.user.stores.first()
        return super().create(validated_data)


class ProductHistorySerializer(serializers.ModelSerializer):
    changed_by_name = serializers.CharField(source='changed_by.name', read_only=True, default='System')

    class Meta:
        model = ProductHistory
        fields = [
            'id', 'changed_by_name', 'old_price', 'new_price',
            'old_stock', 'new_stock', 'reason', 'created_at',
        ]