from decimal import Decimal

from django.db import models

from main.models import Product, ProductSize


class Cart(models.Model):
    """Shopping cart connected to an anonymous or authenticated session."""

    session_key = models.CharField(max_length=40, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"Cart {self.session_key}"

    @property
    def total_items(self) -> int:
        """Return the total quantity of all items in the cart."""
        return sum(item.quantity for item in self.items.all())

    @property
    def subtotal(self) -> Decimal:
        """Return the cart subtotal before discounts, taxes or shipping."""
        return sum((item.total_price for item in self.items.all()), Decimal("0"))

    def add_product(
        self,
        product: Product,
        product_size: ProductSize,
        quantity: int = 1,
    ) -> "CartItem":
        """Add a product-size pair to the cart or increase its quantity."""
        if product_size.product.id != product.id:
            raise ValueError("ProductSize does not belong to this product")

        cart_item, is_created = CartItem.objects.get_or_create(
            cart=self,
            product=product,
            product_size=product_size,
            defaults={"quantity": quantity},
        )

        if not is_created:
            cart_item.quantity += quantity
            cart_item.save()

        return cart_item

    def remove_item(self, item_id: int) -> bool:
        """Remove an item by id and report whether it existed."""
        try:
            item = self.items.get(id=item_id)
            item.delete()
        except CartItem.DoesNotExist:
            return False
        else:
            return True

    def update_item_quantity(self, item_id: int, quantity: int) -> bool:
        """Update an item quantity, deleting the item when quantity is zero."""
        try:
            item = self.items.get(id=item_id)
            if quantity > 0:
                item.quantity = quantity
                item.save()
            else:
                item.delete()
        except CartItem.DoesNotExist:
            return False
        else:
            return True

    def clear(self) -> None:
        """Remove every item from the cart."""
        self.items.all().delete()


class CartItem(models.Model):
    """One product-size line item inside a shopping cart."""

    cart = models.ForeignKey(Cart, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    product_size = models.ForeignKey(ProductSize, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["cart", "product", "product_size"],
                name="unique_cart_product_size",
            ),
            models.CheckConstraint(
                condition=models.Q(quantity__gt=0),
                name="cart_item_quantity_gt_0",
            ),
        ]
        verbose_name = "Cart item 🌑"
        verbose_name_plural = "Cart items ☀️"

    def __str__(self) -> str:
        return f"{self.product.name} - {self.product_size.size.name} x {self.quantity}"

    @property
    def total_price(self) -> Decimal:
        """Return the total price for this line item."""
        return Decimal(str(self.product.price)) * self.quantity
