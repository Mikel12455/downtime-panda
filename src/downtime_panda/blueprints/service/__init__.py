"""This module defines the service blueprint and models for Downtime Panda's service management."""

__all__ = ["service_blueprint", "Service", "Ping"]

from .models import Ping, Service
from .views import service_blueprint
