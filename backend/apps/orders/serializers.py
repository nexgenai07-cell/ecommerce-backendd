# PATH: apps/orders/serializers.py

from rest_framework import serializers
from .models import Customer, Order, OrderItem, Payment


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = [
            "id",
            "product",
            "product_name",
            "price",
            "quantity",
            "total_price",
        ]


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            "id",
            "stripe_payment_intent_id",
            "status",
            "amount",
            "paid_at",
        ]


class OrderListSerializer(serializers.ModelSerializer):
    """Lightweight — used for order history list (My Orders, API 53)"""

    item_count = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            "id",
            "order_number",
            "total_amount",
            "discount_amount",
            "status",
            "item_count",
            "created_at",
        ]

    def get_item_count(self, obj):
        return obj.items.count()


class AdminOrderListSerializer(serializers.ModelSerializer):
    """
    NEW (Postman testing — 09 Jul 2026): used ONLY for admin order
    listing/filtering (API 57, 58). Doc requires a nested
    "customer": {"name", "phone"} object here — unlike OrderListSerializer
    (My Orders, API 53) where the logged-in customer doesn't need their
    own info echoed back. Kept as a separate serializer instead of adding
    "customer" to OrderListSerializer so API 53's response shape doesn't
    change.
    """

    customer = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            "id",
            "order_number",
            "customer",
            "total_amount",
            "discount_amount",
            "status",
            "created_at",
        ]

    def get_customer(self, obj):
        return {
            "name": obj.customer.name,
            "phone": obj.customer.phone,
        }


class OrderDetailSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source="customer.name", read_only=True)
    customer_email = serializers.EmailField(source="customer.email", read_only=True)
    customer_phone = serializers.CharField(source="customer.phone", read_only=True)

    # Nested serializers
    items = OrderItemSerializer(many=True, read_only=True)
    payment = PaymentSerializer(read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "order_number",
            "status",
            "total_amount",
            "discount_amount",
            "shipping_address",
            "tracking_number",
            "notes",
            "created_at",
            "updated_at",

            "customer_name",
            "customer_email",
            "customer_phone",

            "items",
            "payment",
        ]
        
class CheckoutSerializer(serializers.Serializer):
    """POST /api/v1/orders/checkout/"""

    shipping_address = serializers.CharField()
    notes = serializers.CharField(
        required=False,
        allow_blank=True,
    )


class AdminOrderStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(
        choices=[
            "pending_payment",
            "confirmed",
            "shipped",
            "delivered",
            "cancelled",
        ]
    )
    tracking_number = serializers.CharField(
        required=False,
        allow_blank=True,
    )