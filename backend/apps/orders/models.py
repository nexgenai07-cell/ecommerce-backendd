# PATH: apps/orders/models.py

from django.db import models
from django.conf import settings

# Stores customer information for each store.
# One user can have different customer profiles in different stores.
class Customer(models.Model):
    """Store-specific customer profile, auto-created on first order"""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="customer_profiles",
    )

    store = models.ForeignKey(
        "stores.Store",
        on_delete=models.CASCADE,
        related_name="customers",
    )

    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    email = models.EmailField(null=True, blank=True)
    address = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

# Prevents duplicate customer profiles for the same user or phone number within a store.
    class Meta:
        db_table = "customers"
        unique_together = [
            ("user", "store"),
            ("phone", "store"),
        ]

# Returns customer's name and phone number.
    def __str__(self):
        return f"{self.name} ({self.phone})"

# Stores the main order information after checkout.
class Order(models.Model):
    # Defines all possible order statuses.
    STATUS_CHOICES = [
        ("pending_payment", "Pending Payment"),
        ("confirmed", "Confirmed"),
        ("shipped", "Shipped"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
    ]

    store = models.ForeignKey(
        "stores.Store",
        on_delete=models.CASCADE,
        related_name="orders",
    )

    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name="orders",
    )

    order_number = models.CharField(max_length=20, unique=True)

    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    discount_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending_payment",
    )

    shipping_address = models.TextField()

    tracking_number = models.CharField(
        max_length=100,
        null=True,
        blank=True,
    )

    notes = models.TextField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

# Orders are displayed with newest orders first.
    class Meta:
        db_table = "orders"
        ordering = ["-created_at"]

# Returns the order number for easy identification.
    def __str__(self):
        return self.order_number

# Stores every product purchased in an order.
# Each row represents one product inside an order.
class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
    )

    product = models.ForeignKey(
        "products.Product",
        on_delete=models.SET_NULL,
        null=True,
    )

    product_name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = "order_items"

# Returns quantity and product name.
    def __str__(self):
        return f"{self.quantity} x {self.product_name}"

# Stores payment information for each order.
# One payment record exists for one order.
class Payment(models.Model):
    # Defines different payment statuses.
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("paid", "Paid"),
        ("failed", "Failed"),
        ("refunded", "Refunded"),
    ]

    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name="payment",
    )

    stripe_payment_intent_id = models.CharField(
        max_length=255,
        unique=True,
        null=True,
        blank=True,
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    paid_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "payments"
# Returns payment information using order number.
    def __str__(self):
        return f"Payment for {self.order.order_number}"