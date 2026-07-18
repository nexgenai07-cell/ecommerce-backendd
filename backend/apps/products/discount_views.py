from rest_framework import viewsets, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Discount
from .discount_serializers import (
    DiscountSerializer,
    DiscountValidateSerializer,
)
from apps.users.permissions import IsAdmin


class DiscountViewSet(viewsets.ModelViewSet):
    """
    GET/POST    /api/v1/discounts/
    GET/PUT/DELETE /api/v1/discounts/{id}/

    Admin only.

    DELETE is a SOFT DELETE:
    Instead of removing the row, is_active=False.
    """

    serializer_class = DiscountSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]
    pagination_class = None

    def get_queryset(self):
        # Admin sees both active and inactive discounts
        return Discount.objects.all().order_by("-created_at")

    def perform_destroy(self, instance):
        """
        Soft delete instead of permanently deleting.
        """
        instance.is_active = False
        instance.save(update_fields=["is_active"])


class DiscountValidateView(APIView):
    """
    POST /api/v1/discounts/validate/

    Validate a coupon during checkout.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = DiscountValidateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        discount = serializer.validated_data["discount"]
        order_amount = serializer.validated_data["order_amount"]

        if discount.type == "percent":
            discount_amount = (order_amount * discount.value) / 100
        else:
            discount_amount = discount.value

        # Discount cannot exceed order amount
        discount_amount = min(discount_amount, order_amount)

        return Response(
            {
                "valid": True,
                "code": discount.code,
                "discount_type": discount.type,
                "discount_value": discount.value,
                "discount_amount": round(discount_amount, 2),
                "final_amount": round(order_amount - discount_amount, 2),
            },
            status=status.HTTP_200_OK,
        )