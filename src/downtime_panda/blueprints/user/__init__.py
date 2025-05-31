"""
The user package provides functionality related to user management,
including user views and blueprints for integration with the main application.
"""

__all__ = ["User", "user_blueprint"]

from .models import User
from .views import user_blueprint
