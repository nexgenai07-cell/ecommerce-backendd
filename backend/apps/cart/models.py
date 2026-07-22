from django.db import models
from django.conf import settings


class Cart(models.Model):
    # User is optional so anonymous users can also have carts
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="carts",
        null=True,
        blank=True,
    )

    # Used for anonymous users
    session_key = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        db_index=True,
    )

    store = models.ForeignKey(
        "stores.Store",
        on_delete=models.CASCADE,
    )

    coupon = models.ForeignKey(
        "products.Discount",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "carts"

        constraints = [
            models.UniqueConstraint(
                fields=["user", "store"],
                condition=models.Q(user__isnull=False),
                name="unique_user_cart_per_store",
            ),
            models.UniqueConstraint(
                fields=["session_key", "store"],
                condition=models.Q(session_key__isnull=False),
                name="unique_session_cart_per_store",
            ),
        ]

    def __str__(self):
        if self.user:
            return f"Cart of {self.user.email}"
        return f"Cart of session {self.session_key}"

    @property
    def subtotal(self):
        return sum(item.total_price for item in self.items.all())

    @property
    def discount_amount(self):
        if not self.coupon:
            return 0

        if self.coupon.type == "percent":
            return round(self.subtotal * self.coupon.value / 100, 2)

        return min(self.coupon.value, self.subtotal)

    @property
    def total(self):
        return max(self.subtotal - self.discount_amount, 0)


class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name="items",
    )

    product = models.ForeignKey(
        "products.Product",
        on_delete=models.CASCADE,
    )

    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "cart_items"
        unique_together = ["cart", "product"]

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    @property
    def total_price(self):
        return self.product.price * self.quantity


class Wishlist(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="wishlists",
    )

    store = models.ForeignKey(
        "stores.Store",
        on_delete=models.CASCADE,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "wishlists"
        unique_together = ["user", "store"]

    def __str__(self):
        return f"Wishlist of {self.user.email}"


class WishlistItem(models.Model):
    wishlist = models.ForeignKey(
        Wishlist,
        on_delete=models.CASCADE,
        related_name="items",
    )

    product = models.ForeignKey(
        "products.Product",
        on_delete=models.CASCADE,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "wishlist_items"
        unique_together = ["wishlist", "product"]

    def __str__(self):
        return f"{self.product.name} in wishlist"