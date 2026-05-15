from typing import Any

from django import template

from cart.models import Cart

register = template.Library()


@register.simple_tag(takes_context=True)
def get_cart_count(context: dict[str, Any]) -> int:
    """Return the current session cart item count for templates."""
    request = context["request"]
    if not request.session.session_key:
        return 0

    try:
        cart = Cart.objects.get(session_key=request.session.session_key)
    except Cart.DoesNotExist:
        return 0
    else:
        return cart.total_items


@register.filter
def multiply(value: Any, arg: Any) -> float:
    """Multiply two template values and return zero when conversion fails."""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0
