from django.db import transaction
from django.http import HttpRequest, JsonResponse
from django.http.response import HttpResponseBase
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.views.generic import View

from main.models import Product, ProductSize

from .forms import AddToCartForm, UpdateCartItemForm
from .models import Cart, CartItem


class CartMixin:
    """Shared helper for resolving the current session cart."""

    def get_cart(self, request: HttpRequest) -> Cart:
        """Return the cart attached by middleware or create one for the session."""
        if hasattr(request, "cart"):
            return request.cart

        if not request.session.session_key:
            request.session.create()

        cart, _created = Cart.objects.get_or_create(
            session_key=request.session.session_key
        )

        request.session["cart_id"] = cart.id
        request.session.modified = True
        return cart


class CartModalView(CartMixin, View):
    """Render the cart modal content."""

    def get(self, request: HttpRequest) -> TemplateResponse:
        """Return cart items ordered by newest first."""
        cart = self.get_cart(request)
        context = {
            "cart": cart,
            "cart_items": cart.items.select_related(
                "product", "product_size__size"
            ).order_by("-added_at"),
        }
        return TemplateResponse(request, "cart/cart_modal.html", context)


class AddToCartView(CartMixin, View):
    """Add a product to the current cart."""

    @transaction.atomic
    def post(self, request: HttpRequest, slug: str) -> HttpResponseBase:
        """Validate stock and add the selected product-size pair."""
        cart = self.get_cart(request)
        product = get_object_or_404(Product, slug=slug)

        form = AddToCartForm(request.POST, product=product)

        if not form.is_valid():
            return JsonResponse(
                {
                    "error": "Некорректные данные формы",
                    "errors": form.errors,
                },
                status=400,
            )

        size_id = form.cleaned_data.get("size_id")
        if size_id:
            product_size = get_object_or_404(ProductSize, id=size_id, product=product)
        else:
            product_size = product.product_sizes.filter(stock__gt=0).first()
            if not product_size:
                return JsonResponse({"error": "Нет доступных размеров"}, status=400)

        quantity = form.cleaned_data["quantity"]
        if product_size.stock < quantity:
            return JsonResponse(
                {"error": f"Доступно только {product_size.stock} шт."},
                status=400,
            )

        existing_item = cart.items.filter(
            product=product,
            product_size=product_size,
        ).first()

        if existing_item:
            total_quantity = existing_item.quantity + quantity
            if total_quantity > product_size.stock:
                available_quantity = product_size.stock - existing_item.quantity
                return JsonResponse(
                    {
                        "error": (
                            f"Нельзя добавить {quantity} шт. "
                            f"Доступно еще только {available_quantity} шт."
                        )
                    },
                    status=400,
                )

        cart_item = cart.add_product(product, product_size, quantity)

        request.session["cart_id"] = cart.id
        request.session.modified = True

        if request.headers.get("HX-Request"):
            return redirect("cart:cart_modal")
        return JsonResponse(
            {
                "success": True,
                "total_items": cart.total_items,
                "message": f"{product.name} добавлен в корзину",
                "cart_item_id": cart_item.id,
            }
        )


class UpdateCartItemView(CartMixin, View):
    """Update the quantity of one cart item."""

    @transaction.atomic
    def post(self, request: HttpRequest, item_id: int) -> HttpResponseBase:
        """Validate and persist a cart item quantity change."""
        cart = self.get_cart(request)
        cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)

        form = UpdateCartItemForm(request.POST, instance=cart_item)

        if not form.is_valid():
            return JsonResponse({"errors": form.errors}, status=400)

        quantity = form.cleaned_data["quantity"]

        if quantity < 0:
            return JsonResponse({"error": "Некорректное количество"}, status=400)

        if quantity == 0:
            cart_item.delete()
        else:
            if quantity > cart_item.product_size.stock:
                return JsonResponse(
                    {"error": f"Доступно только {cart_item.product_size.stock} шт."},
                    status=400,
                )

            cart_item.quantity = quantity
            cart_item.save()

        request.session["cart_id"] = cart.id
        request.session.modified = True

        context = {
            "cart": cart,
            "cart_items": cart.items.select_related(
                "product",
                "product_size__size",
            ).order_by("-added_at"),
        }
        return TemplateResponse(request, "cart/cart_modal.html", context)


class RemoveCartItemView(CartMixin, View):
    """Remove a cart item from the current cart."""

    def post(self, request: HttpRequest, item_id: int) -> HttpResponseBase:
        """Delete an item and return the refreshed cart modal."""
        cart = self.get_cart(request)

        try:
            cart_item = cart.items.get(id=item_id)
            cart_item.delete()

            request.session["cart_id"] = cart.id
            request.session.modified = True

            context = {
                "cart": cart,
                "cart_items": cart.items.select_related(
                    "product",
                    "product_size__size",
                ).order_by("-added_at"),
            }
            return TemplateResponse(request, "cart/cart_modal.html", context)
        except CartItem.DoesNotExist:
            return JsonResponse({"error": "Товар не найден"}, status=400)


class CartCountView(CartMixin, View):
    """Return the current cart item count and subtotal as JSON."""

    def get(self, request: HttpRequest) -> JsonResponse:
        """Return lightweight cart data for header updates."""
        cart = self.get_cart(request)
        return JsonResponse(
            {"total_items": cart.total_items, "subtotal": float(cart.subtotal)}
        )


class ClearCartView(CartMixin, View):
    """Remove every item from the current cart."""

    def post(self, request: HttpRequest) -> HttpResponseBase:
        """Clear the cart and return either an HTMX partial or JSON."""
        cart = self.get_cart(request)
        cart.clear()

        request.session["cart_id"] = cart.id
        request.session.modified = True

        if request.headers.get("HX-Request"):
            return TemplateResponse(request, "cart/cart_empty.html", {"cart": cart})
        return JsonResponse({"success": True, "message": "Корзина очищена"})


class CartSummaryView(CartMixin, View):
    """Render a compact cart summary partial."""

    def get(self, request: HttpRequest) -> TemplateResponse:
        """Return cart summary items ordered by newest first."""
        cart = self.get_cart(request)
        context = {
            "cart": cart,
            "cart_items": cart.items.select_related(
                "product", "product_size__size"
            ).order_by("-added_at"),
        }
        return TemplateResponse(request, "cart/cart_summary.html", context)
