# PATH: ecommerce/apps/cart/models.py

from django.db import models
from django.conf import settings


class Cart(models.Model):
    user       = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='carts')
    store      = models.ForeignKey('stores.Store', on_delete=models.CASCADE)
    coupon     = models.ForeignKey('products.Discount', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table        = 'carts'
        unique_together = ['user', 'store']  # one cart per user per store

    def __str__(self):
        return f'Cart of {self.user.email}'

    @property
    def subtotal(self):
        return sum(item.total_price for item in self.items.all())

    @property
    def discount_amount(self):
        if not self.coupon:
            return 0
        if self.coupon.type == 'percent':
            return round(self.subtotal * self.coupon.value / 100, 2)
        return min(self.coupon.value, self.subtotal)

    @property
    def total(self):
        return max(self.subtotal - self.discount_amount, 0)


class CartItem(models.Model):
    cart       = models.ForeignKey(Cart,                   on_delete=models.CASCADE, related_name='items')
    product    = models.ForeignKey('products.Product',     on_delete=models.CASCADE)
    quantity   = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table        = 'cart_items'
        unique_together = ['cart', 'product']

    def __str__(self):
        return f'{self.quantity} x {self.product.name}'

    @property
    def total_price(self):
        return self.product.price * self.quantity


class Wishlist(models.Model):
    user       = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wishlists')
    store      = models.ForeignKey('stores.Store', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table        = 'wishlists'
        unique_together = ['user', 'store']

    def __str__(self):
        return f'Wishlist of {self.user.email}'


class WishlistItem(models.Model):
    wishlist   = models.ForeignKey(Wishlist,           on_delete=models.CASCADE, related_name='items')
    product    = models.ForeignKey('products.Product', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table        = 'wishlist_items'
        unique_together = ['wishlist', 'product']