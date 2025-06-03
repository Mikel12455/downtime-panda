"""Defines the Flask application factory for Downtime Panda."""

__all__ = ["create_app"]

import os

from flask import Flask

from . import extensions
from .blueprints.api.routes import api_blueprint
from .blueprints.home.routes import home_blueprint
from .blueprints.service.routes import service_api_blueprint, service_blueprint
from .blueprints.user.routes import user_blueprint
from .config import Config


def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)

    # ------------------------------- CONFIGURATION ------------------------------ #
    app.logger.info("Configuring Downtime Panda application...")
    app.config.from_object(Config())

    # -------------------------------- EXTENSIONS -------------------------------- #
    app.logger.info("Initializing extensions...")
    extensions.login_manager.init_app(app)
    extensions.db.init_app(app)
    extensions.migrate.init_app(app, extensions.db)
    extensions.scheduler.init_app(app)
    extensions.moment.init_app(app)

    # -------------------------------- BLUEPRINTS -------------------------------- #
    app.logger.info("Registering blueprints...")
    app.register_blueprint(home_blueprint, url_prefix="/")
    app.register_blueprint(user_blueprint, url_prefix="/user")
    app.register_blueprint(service_blueprint, url_prefix="/service")
    app.register_blueprint(service_api_blueprint, url_prefix="/api/service")
    app.register_blueprint(api_blueprint, url_prefix="/api")

    # -------------------------- SCHEDULER CONFIGURATION ------------------------- #
    if (
        not (app.debug or app.config["DEBUG"])
        or os.environ.get("WERKZEUG_RUN_MAIN") == "true"
    ):
        app.logger.info("Configuring APScheduler...")
        extensions.scheduler.start()
        app.logger.info(extensions.scheduler.scheduler._jobstores)

    app.logger.info("Downtime Panda application configured successfully.")
    return app
