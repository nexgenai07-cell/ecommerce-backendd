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
    Used for Admin Order List and Admin Order Filter APIs.
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
            "id": obj.customer.id,
            "name": obj.customer.name,
            "phone": obj.customer.phone,
        }


class OrderDetailSerializer(serializers.ModelSerializer):
    customer = serializers.SerializerMethodField()

    items = OrderItemSerializer(
        many=True,
        read_only=True,
    )

    payment = PaymentSerializer(
        read_only=True,
    )

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

            "customer",

            "items",
            "payment",
        ]

    def get_customer(self, obj):
        return {
            "id": obj.customer.id,
            "name": obj.customer.name,
            "email": obj.customer.email,
            "phone": obj.customer.phone,
        }
        
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