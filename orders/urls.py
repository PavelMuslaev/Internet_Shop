"""URL routes for the orders application."""

from django.urls import path
from .views import CheckoutView

app_name = 'orders'

urlpatterns = [
    path('checkout/', CheckoutView.as_view(), name='checkout'),
]
