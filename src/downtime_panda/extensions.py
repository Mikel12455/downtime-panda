"""Extensions for Flask applications."""

from flask_apscheduler import APScheduler
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase


# -------------------------------- SQLALCHEMY -------------------------------- #
class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)

# ----------------------------------- LOGIN ---------------------------------- #
login_manager = LoginManager()

# -------------------------------- APSCHEDULER ------------------------------- #
scheduler = APScheduler()
