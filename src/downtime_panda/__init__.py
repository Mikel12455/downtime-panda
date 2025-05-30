"""Defines the Flask application factory for Downtime Panda."""

__all__ = ["create_app"]

import os

import pytz
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from flask import Flask

from . import extensions
from .config import Config, Consts
from .home import home_blueprint
from .service import service_blueprint
from .user import user_blueprint


def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)

    # ------------------------------- CONFIGURATION ------------------------------ #

    app.config.from_object(Config)

    # -------------------------------- BLUEPRINTS -------------------------------- #

    app.register_blueprint(home_blueprint, url_prefix="/")
    app.register_blueprint(service_blueprint, url_prefix="/service")
    app.register_blueprint(user_blueprint, url_prefix="/user")

    # -------------------------------- EXTENSIONS -------------------------------- #

    extensions.login_manager.init_app(app)
    extensions.db.init_app(app)
    extensions.scheduler.init_app(app)

    with app.app_context():
        extensions.db.create_all()

    # -------------------------- SCHEDULER CONFIGURATION ------------------------- #
    if (
        not (app.debug or app.config["DEBUG"])
        or os.environ.get("WERKZEUG_RUN_MAIN") == "true"
    ):
        jobstore = SQLAlchemyJobStore(
            url=Config.SQLALCHEMY_DATABASE_URI, tableschema=Consts.SCHEMA
        )

        extensions.scheduler.scheduler.add_jobstore(jobstore)
        extensions.scheduler.scheduler.timezone = pytz.utc
        extensions.scheduler.start()

    return app
