# PATH: apps/cart/views.py

from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils import timezone

from .models import Cart, CartItem
from .serializers import (
    CartSerializer, AddToCartSerializer,
    UpdateCartItemSerializer, ApplyCouponSerializer,
)
from apps.products.models import Discount
from apps.stores.models import Store


def get_or_create_cart(user):
    """Each user has exactly one cart — single-store setup always uses the one store"""
    cart, _ = Cart.objects.get_or_create(user=user, defaults={'store': Store.objects.first()})
    return cart


class CartView(APIView):
    """GET /api/v1/cart/"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        cart = get_or_create_cart(request.user)
        return Response(CartSerializer(cart).data)


class AddToCartView(APIView):
    """POST /api/v1/cart/add/"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = AddToCartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product = serializer.validated_data['product']
        quantity = serializer.validated_data['quantity']

        cart = get_or_create_cart(request.user)

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart, product=product,
            defaults={'quantity': quantity}
        )

        if not created:
            new_quantity = cart_item.quantity + quantity
            if new_quantity > product.stock:
                return Response(
                    {'error': f'Only {product.stock} units available in stock.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            cart_item.quantity = new_quantity
            cart_item.save()

        return Response(CartSerializer(cart).data, status=status.HTTP_200_OK)


class UpdateCartItemView(APIView):
    """PUT /api/v1/cart/update/{item_id}/"""
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request, item_id):
        cart = get_or_create_cart(request.user)
        try:
            cart_item = cart.items.get(id=item_id)
        except CartItem.DoesNotExist:
            return Response({'error': 'Cart item not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = UpdateCartItemSerializer(data=request.data, context={'cart_item': cart_item})
        serializer.is_valid(raise_exception=True)
        quantity = serializer.validated_data['quantity']

        if quantity == 0:
            cart_item.delete()
        else:
            cart_item.quantity = quantity
            cart_item.save()

        return Response(CartSerializer(cart).data)


class RemoveCartItemView(APIView):
    """DELETE /api/v1/cart/remove/{item_id}/"""
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, item_id):
        cart = get_or_create_cart(request.user)
        try:
            cart_item = cart.items.get(id=item_id)
        except CartItem.DoesNotExist:
            return Response({'error': 'Cart item not found.'}, status=status.HTTP_404_NOT_FOUND)

        cart_item.delete()
        return Response(CartSerializer(cart).data)


class ClearCartView(APIView):
    """DELETE /api/v1/cart/clear/"""
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request):
        cart = get_or_create_cart(request.user)
        cart.items.all().delete()
        cart.coupon = None
        cart.save()
        return Response({'message': 'Cart cleared.'}, status=status.HTTP_200_OK)


class ApplyCouponView(APIView):
    """POST /api/v1/cart/apply-coupon/"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ApplyCouponSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        code = serializer.validated_data['code']

        try:
            discount = Discount.objects.get(code=code, is_active=True)
        except Discount.DoesNotExist:
            return Response({'error': 'Invalid or inactive coupon code.'}, status=status.HTTP_400_BAD_REQUEST)

        now = timezone.now()
        if not (discount.start_date <= now <= discount.end_date):
            return Response({'error': 'This coupon has expired or is not active yet.'}, status=status.HTTP_400_BAD_REQUEST)

        cart = get_or_create_cart(request.user)
        subtotal = sum(item.product.price * item.quantity for item in cart.items.all())

        if discount.min_order_amount and subtotal < discount.min_order_amount:
            return Response(
                {'error': f'Minimum order amount of Rs. {discount.min_order_amount} required for this coupon.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        cart.coupon = discount
        cart.save()

        return Response(CartSerializer(cart).data)


class RemoveCouponView(APIView):
    """DELETE /api/v1/cart/remove-coupon/"""
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request):
        cart = get_or_create_cart(request.user)
        cart.coupon = None
        cart.save()
        return Response(CartSerializer(cart).data)