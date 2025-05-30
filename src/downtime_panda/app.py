import os


def create_app():
    """Create and configure the Flask application."""
    from flask import Flask

    app = Flask(__name__)

    # ------------------------------- CONFIGURATION ------------------------------ #
    from downtime_panda.config import Config

    app.config.from_object(Config)

    # -------------------------------- BLUEPRINTS -------------------------------- #
    from downtime_panda.home import home_blueprint
    from downtime_panda.service import service_blueprint
    from downtime_panda.user import user_blueprint

    app.register_blueprint(home_blueprint, url_prefix="/")
    app.register_blueprint(service_blueprint, url_prefix="/service")
    app.register_blueprint(user_blueprint, url_prefix="/user")

    # -------------------------------- EXTENSIONS -------------------------------- #
    from . import extensions

    extensions.login_manager.init_app(app)
    extensions.db.init_app(app)

    with app.app_context():
        extensions.db.create_all()

    from .scheduler import scheduler

    if (
        not (app.debug or app.config["DEBUG"])
        or os.environ.get("WERKZEUG_RUN_MAIN") == "true"
    ):
        scheduler.start()

    return app
