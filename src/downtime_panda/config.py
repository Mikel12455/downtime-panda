"""
This module contains both Flask configuration and application constants for Downtime Panda.
"""

import os

import pytz
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore


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

    SQLALCHEMY_DATABASE_URI = (
        f"postgresql+psycopg://{os.getenv('DTPANDA_DB_URL')}"
        if os.getenv("DTPANDA_DB_URL")
        else "sqlite:///dtpanda.db"
    )
    """
    The database connection URL for the database, constructed from the environment variable 'DTPANDA_DB_URL'.

    Defaults to a SQLite database file named `dtpanda.db` if the environment variable is not set, which is saved inside the `src/instance` directory.
    """

    SECRET_KEY = os.getenv("DTPANDA_SECRET_KEY") or "a_very_secret_key"
    """
    The secret key used by Flask for cryptographic operations (e.g., session signing).
    Loaded from the environment variable 'DTPANDA_SECRET'.
    """

    # -------------------------------- APSCHEDULER ------------------------------- #
    SCHEDULER_JOBSTORES = {
        "default": SQLAlchemyJobStore(
            url=SQLALCHEMY_DATABASE_URI
            if os.getenv("DTPANDA_DB_URL")
            else "sqlite:///src/instance/dtpanda.db",
            tablename="apscheduler_jobs",
        ),
    }
    """
    Configuration for the APScheduler job store.
    """

    SCHEDULER_TIMEZONE = pytz.utc
    """
    The timezone used by the APScheduler.
    Set to UTC by default.
    """


class TestingConfig(Config):
    """
    Configuration class for testing environment.
    Inherits from Config and overrides specific settings for testing.
    """

    DEBUG = True
    """
    Enables debug mode for testing.
    """

    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    """
    Uses an in-memory SQLite database for testing purposes.
    This allows for fast tests without needing a persistent database.
    """

    TESTING = True
    """
    Indicates that the application is in testing mode.
    This can enable additional testing features or behaviors.
    """

    WTF_CSRF_ENABLED = False
    """
    Disables CSRF protection for testing.
    This is often done in tests to simplify form submissions.
    """
