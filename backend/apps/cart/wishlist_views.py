# PATH: apps/cart/wishlist_views.py

from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Wishlist, WishlistItem
from .wishlist_serializers import WishlistSerializer, AddToWishlistSerializer
from apps.stores.models import Store


def get_or_create_wishlist(user):
    wishlist, _ = Wishlist.objects.get_or_create(user=user, defaults={'store': Store.objects.first()})
    return wishlist


class WishlistView(APIView):
    """GET /api/v1/wishlist/"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        wishlist = get_or_create_wishlist(request.user)
        return Response(WishlistSerializer(wishlist).data)


class AddToWishlistView(APIView):
    """POST /api/v1/wishlist/add/"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = AddToWishlistSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product_id = serializer.validated_data['product_id']

        wishlist = get_or_create_wishlist(request.user)
        WishlistItem.objects.get_or_create(wishlist=wishlist, product_id=product_id)

        return Response(WishlistSerializer(wishlist).data, status=status.HTTP_200_OK)


class RemoveFromWishlistView(APIView):
    """DELETE /api/v1/wishlist/remove/{item_id}/"""
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, item_id):
        wishlist = get_or_create_wishlist(request.user)
        try:
            item = wishlist.items.get(id=item_id)
        except WishlistItem.DoesNotExist:
            return Response({'error': 'Wishlist item not found.'}, status=status.HTTP_404_NOT_FOUND)

        item.delete()
        return Response(WishlistSerializer(wishlist).data)