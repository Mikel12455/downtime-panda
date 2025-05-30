"""
This module contains both Flask configuration and application constants for Downtime Panda.
"""

import os


class Config:
    """
    Configuration class for the Downtime Panda application.
    This class holds configuration settings such as debug mode, database URL, and secret key.
    """

    DEBUG = os.getenv("DTPANDA_DEBUG", "false").lower() in ("true", "1", "yes")
    """
    Indicates whether the application is running in debug mode.
    Set to True if the environment variable 'DTPANDA_DEBUG' is set to 'true', '1', or 'yes' (case-insensitive).
    """

    SQLALCHEMY_DATABASE_URI = f"postgresql+psycopg://{os.getenv('DTPANDA_DB_URL')}"
    """
    The database connection URL for PostgreSQL using the psycopg driver.
    Constructed from the environment variable 'DTPANDA_DB_URL'.
    """

    SECRET_KEY = os.getenv("DTPANDA_SECRET_KEY")
    """
    The secret key used by Flask for cryptographic operations (e.g., session signing).
    Loaded from the environment variable 'DTPANDA_SECRET'.
    """


class Consts:
    """
    Constants used throughout the Downtime Panda application.
    """

    SCHEMA = "downtime_panda"
    """
    The schema name used in the database for storing application data.
    """
