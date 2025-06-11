"""
Defines the Flask application factory for Downtime Panda.

exports:
    - create_app: Function to create and configure the Flask application.
"""

__all__ = ["create_app"]

import logging
import os

from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from flask import Flask
from loguru import logger

from downtime_panda import extensions
from downtime_panda.blueprints.home.routes import home_blueprint
from downtime_panda.blueprints.service.routes import service_blueprint
from downtime_panda.blueprints.subscription.api import subscription_api_blueprint
from downtime_panda.blueprints.subscription.routes import subscription_blueprint
from downtime_panda.blueprints.token.routes import token_blueprint
from downtime_panda.blueprints.user.routes import user_blueprint
from downtime_panda.config import Config


def create_app(config_class=Config):
    """Create and configure the Flask application."""
    app = Flask(__name__)

    # ---------------------------------- LOGGING --------------------------------- #
    class InterceptHandler(logging.Handler):
        def emit(self, record):
            # Retrieve context where the logging call occurred, this happens to be in the 6th frame upward
            logger_opt = logger.opt(depth=6, exception=record.exc_info)
            logger_opt.log(record.levelno, record.getMessage())

    handler = InterceptHandler()
    app.logger.addHandler(handler)

    from flask.logging import default_handler

    app.logger.removeHandler(default_handler)

    # ------------------------------- CONFIGURATION ------------------------------ #
    logger.info("Setting up configuration...")
    app.config.from_object(config_class())

    # -------------------------------- EXTENSIONS -------------------------------- #
    logger.info("Initializing extensions...")
    extensions.login_manager.init_app(app)
    extensions.db.init_app(app)
    extensions.migrate.init_app(app, extensions.db)
    with app.app_context():
        app.config["SCHEDULER_JOBSTORES"] = {
            "default": SQLAlchemyJobStore(
                engine=extensions.db.engine,
                tablename="apscheduler_jobs",
            ),
        }
    extensions.scheduler.init_app(app)
    extensions.moment.init_app(app)

    with app.app_context():
        logger.info("Creating database tables...")
        extensions.db.create_all()

    # -------------------------------- BLUEPRINTS -------------------------------- #
    logger.info("Registering blueprints...")
    app.register_blueprint(home_blueprint, url_prefix="/")
    app.register_blueprint(user_blueprint, url_prefix="/user")
    app.register_blueprint(service_blueprint, url_prefix="/service")
    app.register_blueprint(subscription_api_blueprint, url_prefix="/api/service")
    app.register_blueprint(subscription_blueprint, url_prefix="/subscription")
    app.register_blueprint(token_blueprint, url_prefix="/you/tokens")

    # -------------------------- SCHEDULER CONFIGURATION ------------------------- #
    if (
        not (app.debug or app.config["DEBUG"])
        or os.environ.get("WERKZEUG_RUN_MAIN") == "true"
    ):
        logger.info("Starting APScheduler...")
        extensions.scheduler.start()
        logger.info(extensions.scheduler.scheduler._jobstores)

    logger.info("Downtime Panda application configured successfully.")
    return app
