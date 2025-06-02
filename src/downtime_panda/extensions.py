"""Extensions for Flask applications."""

from flask_apscheduler import APScheduler
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import declarative_base

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
