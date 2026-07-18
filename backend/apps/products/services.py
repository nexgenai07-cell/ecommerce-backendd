from django.db import transaction
from django.db.models import F

from .models import Product, StockMovement


# Safely updates product stock and records every stock movement.
def adjust_stock(
    *,
    product,
    delta,
    reason,
    changed_by=None,
    note=""
):
    """
    Atomically adjust product stock and record a StockMovement.
    """

    if delta == 0:
        raise ValueError("delta cannot be 0.")

# Executes all database operations as a single transaction.
    with transaction.atomic():

        # Lock this product row until transaction completes
        product = (  
            Product.objects
            .select_for_update()  # Locks the product row to prevent simultaneous stock updates.
            .get(pk=product.pk)
        )
     
        previous_stock = product.stock # Stores the current stock before making any changes.

        if previous_stock + delta < 0:  # Prevents stock from becoming negative.
            raise ValueError(
                f"Cannot reduce stock below 0. "
                f"Current stock: {previous_stock}, "
                f"requested change: {delta}"
            )

# Updates stock directly inside the database to avoid race conditions.
        Product.objects.filter(
            pk=product.pk
        ).update(
            stock=F("stock") + delta
        )

        product.refresh_from_db() # Reloads the updated product from the database.

# Saves a complete audit record for this stock adjustment.
        StockMovement.objects.create(
            product=product,
            changed_by=changed_by,
            old_stock=previous_stock,
            new_stock=product.stock,
            delta=delta,
            reason=reason,
            note=note,
        )

# Returns updated stock information to the API.
        return {
            "id": product.id,
            "stock": product.stock,
            "previous_stock": previous_stock,
            "delta_applied": delta,
        }