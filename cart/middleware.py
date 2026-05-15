from django.http import HttpRequest
from django.utils.deprecation import MiddlewareMixin

from .models import Cart


class CartMiddleware(MiddlewareMixin):
    """Attach the current session cart to every request."""

    def process_request(self, request: HttpRequest) -> None:
        """Create a session cart when needed and store it on request.cart."""
        if not request.session.session_key:
            request.session.create()

        request.cart, _created = Cart.objects.get_or_create(
            session_key=request.session.session_key
        )
        return None
