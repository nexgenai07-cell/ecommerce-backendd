# PATH: apps/cart/serializers.py

from rest_framework import serializers
from .models import Cart, CartItem
from apps.products.models import Product


class CartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_price = serializers.DecimalField(source='product.price', max_digits=10, decimal_places=2, read_only=True)
    product_image = serializers.SerializerMethodField()
    product_stock = serializers.IntegerField(source='product.stock', read_only=True)
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = [
            'id', 'product', 'product_name', 'product_price',
            'product_image', 'product_stock', 'quantity', 'subtotal', 'created_at',
        ]

    def get_product_image(self, obj):
        img = obj.product.primary_image
        return img.image_url if img else None

    def get_subtotal(self, obj):
        return obj.product.price * obj.quantity


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    subtotal = serializers.SerializerMethodField()
    discount_amount = serializers.SerializerMethodField()
    total = serializers.SerializerMethodField()
    coupon_code = serializers.CharField(source='coupon.code', read_only=True, default=None)

    class Meta:
        model = Cart
        fields = ['id', 'items', 'coupon_code', 'subtotal', 'discount_amount', 'total', 'created_at', 'updated_at']

    def get_subtotal(self, obj):
        return sum(item.product.price * item.quantity for item in obj.items.all())

    def get_discount_amount(self, obj):
        subtotal = self.get_subtotal(obj)
        if not obj.coupon:
            return 0
        if obj.coupon.type == 'percent':
            amount = (subtotal * obj.coupon.value) / 100
        else:
            amount = obj.coupon.value
        return min(amount, subtotal)

    def get_total(self, obj):
        return self.get_subtotal(obj) - self.get_discount_amount(obj)


class AddToCartSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1, default=1)

    def validate(self, data):
        try:
            product = Product.objects.get(id=data['product_id'], is_active=True)
        except Product.DoesNotExist:
            raise serializers.ValidationError({'product_id': 'Product not found.'})

        if product.stock < data['quantity']:
            raise serializers.ValidationError({
                'quantity': f'Only {product.stock} units available in stock.'
            })

        data['product'] = product
        return data


class UpdateCartItemSerializer(serializers.Serializer):
    quantity = serializers.IntegerField(min_value=0)  # 0 means remove

    def validate_quantity(self, value):
        cart_item = self.context.get('cart_item')
        if value > 0 and cart_item and value > cart_item.product.stock:
            raise serializers.ValidationError(
                f'Only {cart_item.product.stock} units available in stock.'
            )
        return value


class ApplyCouponSerializer(serializers.Serializer):
    code = serializers.CharField()