from typing import Any

from django.http import HttpRequest


def cart_processor(request: HttpRequest) -> dict[str, Any]:
    """Expose cart totals to every template."""
    cart = getattr(request, "cart", None)

    return {
        "cart_total_items": cart.total_items if cart else 0,
        "cart_subtotal": cart.subtotal if cart else 0,
    }
