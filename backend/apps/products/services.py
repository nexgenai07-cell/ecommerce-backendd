from django.db import transaction
from django.db.models import F

from .models import Product, StockMovement


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

    with transaction.atomic():

        # Lock this product row until transaction completes
        product = (
            Product.objects
            .select_for_update()
            .get(pk=product.pk)
        )

        previous_stock = product.stock

        if previous_stock + delta < 0:
            raise ValueError(
                f"Cannot reduce stock below 0. "
                f"Current stock: {previous_stock}, "
                f"requested change: {delta}"
            )

        Product.objects.filter(
            pk=product.pk
        ).update(
            stock=F("stock") + delta
        )

        product.refresh_from_db()

        StockMovement.objects.create(
            product=product,
            changed_by=changed_by,
            old_stock=previous_stock,
            new_stock=product.stock,
            delta=delta,
            reason=reason,
            note=note,
        )

        return {
            "id": product.id,
            "stock": product.stock,
            "previous_stock": previous_stock,
            "delta_applied": delta,
        }