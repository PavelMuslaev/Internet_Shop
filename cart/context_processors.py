def cart_processor(request):
    cart = getattr(request, "cart", None)

    return {
        "cart_total_items": cart.total_items if cart else 0,
        "cart_subtotal": cart.subtotal if cart else 0,
    }
