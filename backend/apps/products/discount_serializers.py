# PATH: apps/products/discount_serializers.py
# (kept in a separate file for clarity — import both serializers.py and this in views)

from rest_framework import serializers
from django.utils import timezone
from .models import Discount


class DiscountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Discount
        fields = [
            'id', 'code', 'type', 'value', 'min_order_amount',
            'start_date', 'end_date', 'is_active', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate(self, data):
        start = data.get('start_date', getattr(self.instance, 'start_date', None))
        end = data.get('end_date', getattr(self.instance, 'end_date', None))
        if start and end and start >= end:
            raise serializers.ValidationError('End date must be after start date.')
        return data

    def create(self, validated_data):
        request = self.context['request']
        validated_data['store'] = request.user.stores.first()
        return super().create(validated_data)


class DiscountValidateSerializer(serializers.Serializer):
    """Used for POST /api/v1/discounts/validate/"""
    code = serializers.CharField()
    order_amount = serializers.DecimalField(max_digits=10, decimal_places=2)

    def validate(self, data):
        try:
            discount = Discount.objects.get(code=data['code'], is_active=True)
        except Discount.DoesNotExist:
            raise serializers.ValidationError({'code': 'Invalid or inactive coupon code.'})

        now = timezone.now()
        if not (discount.start_date <= now <= discount.end_date):
            raise serializers.ValidationError({'code': 'This coupon has expired or is not active yet.'})

        if discount.min_order_amount and data['order_amount'] < discount.min_order_amount:
            raise serializers.ValidationError({
                'order_amount': f'Minimum order amount of Rs. {discount.min_order_amount} required for this coupon.'
            })

        data['discount'] = discount
        return data