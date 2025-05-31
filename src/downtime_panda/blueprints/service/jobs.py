from datetime import datetime

import pytz
import requests
from flask import current_app
from sqlalchemy import select

from downtime_panda.blueprints.service import Ping, Service
from downtime_panda.extensions import db, scheduler


# ------------------------------- SCHEDULED JOB ------------------------------ #
def ping_service(service_id: int) -> None:
    with scheduler.app.app_context():
        service = db.session.get(Service, service_id)
        current_app.logger.info(service)

        pinged_at = datetime.now(pytz.utc)
        response = requests.head(service.uri)
        ping = Ping(
            service_id=f"ping_service_{service.id}",
            http_status=response.status_code,
            pinged_at=pinged_at,
        )
        service.ping.add(ping)
        db.session.commit()


@scheduler.task(
    trigger="interval",
    id="reschedule_missing_ping_jobs",
    seconds=30,
    misfire_grace_time=900,
)
def reschedule_missing_ping_jobs():
    with scheduler.app.app_context():
        services = db.session.execute(select(Service)).scalars()
        for service in services:
            job_id = f"ping_service_{service.id}"
            if not scheduler.get_job(job_id):
                scheduler.add_job(
                    func=ping_service,
                    trigger="interval",
                    minutes=service.ping_interval_minutes,
                    args=[service.id],
                    id=job_id,
                    replace_existing=True,
                )


# Optionally, schedule this job to run periodically
scheduler.add_job(
    func=reschedule_missing_ping_jobs,
    trigger="interval",
    minutes=10,
    id="reschedule_missing_service_jobs",
    replace_existing=True,
)
