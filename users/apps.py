from django.apps import AppConfig


class UsersConfig(AppConfig):
    """Application configuration for authentication and user profiles."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'
