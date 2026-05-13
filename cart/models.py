from django.db import models
from django.contrib.sessions.models import Session

from main.models import Product, ProductSize
from decimal import Decimal


class Cart(models.Model):
    session_key = models.CharField(max_length=40, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart {self.session_key}"

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())

    @property
    def subtotal(self):
        return sum(item.total_price for item in self.items.all())

    def add_product(self, product: Product, product_size: ProductSize, quantity=1):
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
        try:
            item = self.items.get(id=item_id)
            item.delete()
        except CartItem.DoesNotExist:
            return False
        else:
            return True

    def update_item_quantity(self, item_id: int, quantity: int) -> bool:
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

    def clear(self):
        self.items.all().delete()


class CartItem(models.Model):
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

    def __str__(self):
        return f"{self.product.name} - {self.product_size.size.name} x {self.quantity}"

    @property
    def total_price(self):
        return Decimal(str(self.product.price)) * self.quantity
