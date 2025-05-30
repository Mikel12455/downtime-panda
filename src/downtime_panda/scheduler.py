"""Scheduler for managing background jobs in Downtime Panda."""

import pytz
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.background import BackgroundScheduler

from downtime_panda.config import Config, Consts

jobstore = SQLAlchemyJobStore(
    url=Config.SQLALCHEMY_DATABASE_URI, tableschema=Consts.SCHEMA
)

scheduler = BackgroundScheduler()
scheduler.add_jobstore(jobstore)
scheduler.timezone = pytz.utc
