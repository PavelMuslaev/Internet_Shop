from typing import Any

from django import forms
from django.core.validators import MaxValueValidator

from main.models import Product

from .models import CartItem


class AddToCartForm(forms.Form):
    """Validate product size and quantity before adding an item to the cart."""

    size_id = forms.IntegerField(required=False)
    quantity = forms.IntegerField(min_value=1, initial=1)

    def __init__(
        self,
        *args: Any,
        product: Product | None = None,
        **kwargs: Any,
    ) -> None:
        """Limit size choices to sizes with stock for the selected product."""
        super().__init__(*args, **kwargs)
        self.product = product

        if product:
            sizes = product.product_sizes.filter(stock__gt=0)
            if sizes.exists():
                first_size = sizes.first()
                self.fields["size_id"] = forms.ChoiceField(
                    choices=[(ps.id, ps.size.name) for ps in sizes],
                    required=True,
                    initial=first_size.id if first_size else None,
                )


class UpdateCartItemForm(forms.ModelForm):
    """Validate quantity updates for an existing cart item."""

    class Meta:
        model = CartItem
        fields = ["quantity"]

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Limit the quantity field to the selected size stock."""
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.product_size:
            self.fields["quantity"].validators.append(
                MaxValueValidator(self.instance.product_size.stock)
            )
