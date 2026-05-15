"""Django app configuration for the orders application."""

from django.apps import AppConfig


class OrdersConfig(AppConfig):
    """Application configuration for order checkout and order history data."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'orders'
