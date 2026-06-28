# PATH: apps/orders/serializers.py

from rest_framework import serializers
from .models import Customer, Order, OrderItem, Payment


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'price', 'quantity', 'total_price']


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'method', 'status', 'amount', 'transaction_id', 'paid_at']


class OrderListSerializer(serializers.ModelSerializer):
    """Lightweight — used for order history list"""
    item_count = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'total_amount', 'discount_amount',
            'status', 'payment_method', 'item_count', 'created_at',
        ]

    def get_item_count(self, obj):
        return obj.items.count()


class OrderDetailSerializer(serializers.ModelSerializer):
    """Full detail — used for single order page and tracking"""
    items = OrderItemSerializer(many=True, read_only=True)
    payment = PaymentSerializer(read_only=True)
    customer_name = serializers.CharField(source='customer.name', read_only=True)
    customer_phone = serializers.CharField(source='customer.phone', read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'total_amount', 'discount_amount', 'status',
            'payment_method', 'shipping_address', 'tracking_number', 'notes',
            'customer_name', 'customer_phone', 'items', 'payment',
            'created_at', 'updated_at',
        ]


class CheckoutSerializer(serializers.Serializer):
    """POST /api/v1/orders/checkout/ — order is built from the user's current cart"""
    shipping_address = serializers.CharField()
    payment_method = serializers.ChoiceField(choices=['COD', 'easypaisa', 'card'])
    notes = serializers.CharField(required=False, allow_blank=True)


class AdminOrderStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=['pending', 'confirmed', 'shipped', 'delivered', 'cancelled'])
    tracking_number = serializers.CharField(required=False, allow_blank=True)