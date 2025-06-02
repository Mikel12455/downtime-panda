"""Extensions for Flask applications."""

from flask_apscheduler import APScheduler
from flask_httpauth import HTTPTokenAuth
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import declarative_base
from werkzeug.http import HTTP_STATUS_CODES

# --------------------------------- DATABASE --------------------------------- #
Base = declarative_base()

db = SQLAlchemy(model_class=Base)
migrate = Migrate()

# ----------------------------------- LOGIN ---------------------------------- #
login_manager = LoginManager()
login_manager.login_view = "user.login"

# -------------------------------- APSCHEDULER ------------------------------- #
scheduler = APScheduler()

# ---------------------------------- MOMENT ---------------------------------- #
moment = Moment()

# ------------------------------ HTTP TOKEN AUTH ----------------------------- #
token_auth = HTTPTokenAuth(scheme="Bearer")

from downtime_panda.blueprints.user.models import User  # noqa: E402


@token_auth.verify_token
def verify_token(token):
    return User.get_by_token(token) if token else None


@token_auth.error_handler
def token_auth_error(status):
    payload = {"error": HTTP_STATUS_CODES.get(status, "Unknown error")}
    return payload, status
