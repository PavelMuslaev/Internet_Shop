from typing import Any

from django.db import models
from django.utils.text import slugify


class Category(models.Model):
    """Product category used to group catalog items."""

    name = models.CharField(max_length=100)
    slug = models.CharField(max_length=100, unique=True)

    def save(self, *args: Any, **kwargs: Any) -> None:
        """Populate the slug from the category name when it is not set."""
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name


class Size(models.Model):
    """Available product size option."""

    name = models.CharField(max_length=20)

    def __str__(self) -> str:
        return self.name


class Product(models.Model):
    """Catalog product shown on listing and detail pages."""

    name = models.CharField(max_length=100)
    slug = models.CharField(max_length=100, unique=True)
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="products"
    )
    color = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)
    main_image = models.ImageField(upload_to="products/main/")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args: Any, **kwargs: Any) -> None:
        """Populate the slug from the product name when it is not set."""
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name


class ProductSize(models.Model):
    """Stock amount for a product in a specific size."""

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="product_sizes"
    )
    size = models.ForeignKey(Size, on_delete=models.CASCADE)
    stock = models.PositiveIntegerField(default=0)

    def __str__(self) -> str:
        return f"{self.size.name} ({self.stock} in stock) for {self.product.name}"


class ProductImage(models.Model):
    """Additional product image displayed on the product detail page."""

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="images"
    )
    image = models.ImageField(upload_to="products/extra/")

    def __str__(self) -> str:
        return f"Image for {self.product.name}"
