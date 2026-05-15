"""Django app configuration for the payment application."""

from django.apps import AppConfig


class PaymentConfig(AppConfig):
    """Application configuration for payment provider integrations."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'payment'
