"""
The user package provides functionality related to user management,
including user views and blueprints for integration with the main application.
"""

__all__ = ["auth_blueprint"]

from .routes import auth_blueprint
