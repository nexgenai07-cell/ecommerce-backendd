# PATH: apps/products/discount_views.py

from rest_framework import viewsets, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Discount
from .discount_serializers import DiscountSerializer, DiscountValidateSerializer
from apps.users.permissions import IsAdmin


class DiscountViewSet(viewsets.ModelViewSet):
    """
    GET/POST    /api/v1/discounts/
    GET/PUT/DEL /api/v1/discounts/{id}/
    Admin only for all actions — discounts are not public listing data.
    """
    serializer_class = DiscountSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]

    def get_queryset(self):
        return Discount.objects.all().order_by('-created_at')


class DiscountValidateView(APIView):
    """
    POST /api/v1/discounts/validate/
    Open to any authenticated customer — used at checkout to check a coupon code.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = DiscountValidateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        discount = serializer.validated_data['discount']
        order_amount = serializer.validated_data['order_amount']

        if discount.type == 'percent':
            discount_amount = (order_amount * discount.value) / 100
        else:
            discount_amount = discount.value

        # Discount cannot exceed the order amount itself
        discount_amount = min(discount_amount, order_amount)

        return Response({
            'valid': True,
            'code': discount.code,
            'type': discount.type,
            'discount_amount': round(discount_amount, 2),
            'final_amount': round(order_amount - discount_amount, 2),
        }, status=status.HTTP_200_OK)