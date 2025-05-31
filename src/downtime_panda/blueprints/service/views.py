import time
from datetime import datetime

import pytz
import requests
from apscheduler.triggers.interval import IntervalTrigger
from flask import (
    Blueprint,
    Response,
    abort,
    current_app,
    redirect,
    render_template,
    request,
    stream_with_context,
    url_for,
)

from downtime_panda.extensions import db, scheduler

from .models import Ping, Service

service_blueprint = Blueprint(
    "service", __name__, static_folder="static", template_folder="templates"
)


# ------------------------------- SCHEDULED JOB ------------------------------ #
def ping_service(service_id: int) -> None:
    with scheduler.app.app_context():
        service = db.session.get(Service, service_id)
        current_app.logger.info(service)

        pinged_at = datetime.now(pytz.utc)
        response = requests.head(service.uri)
        ping = Ping(
            service_id=service.id,
            http_status=response.status_code,
            pinged_at=pinged_at,
        )
        service.ping.add(ping)
        db.session.commit()


# ------------------------------------ SSE ----------------------------------- #
def stream(service: Service, last_pinged_at: datetime):
    while True:
        current_app.logger.info("Test")
        new_pings = db.session.scalars(
            service.ping.select()
            .where(Ping.pinged_at > last_pinged_at)
            .order_by(Ping.pinged_at.desc())
        ).all()

        if new_pings:
            last_pinged_at = max(new_pings, key=lambda x: x.pinged_at).pinged_at
            yield f"data: {new_pings[0].dump_json()}\n\n"

        time.sleep(1)


# ---------------------------------------------------------------------------- #
#                                     VIEWS                                    #
# ---------------------------------------------------------------------------- #
@service_blueprint.route("/<int:id>")
def service_detail(id):
    service = db.get_or_404(Service, id)
    return render_template("detail.html.jinja", service=service)


@service_blueprint.route("/stream/<int:id>")
def service_stream(id):
    service = db.get_or_404(Service, id)

    last_ping = db.session.scalars(service.ping.select()).first()

    if not last_ping:
        abort(404)

    last_pinged_at = last_ping.pinged_at

    return Response(
        stream_with_context(stream(service, last_pinged_at)),
        mimetype="text/event-stream",
    )


@service_blueprint.route("/create", methods=["GET", "POST"])
def service_create():
    if request.method == "GET":
        # Render the service creation form
        return render_template("create.html.jinja")

    # Insert a new service into the database
    service = Service(
        name=request.form["name"],
        uri=request.form["uri"],
    )
    db.session.add(service)
    db.session.flush((service,))
    db.session.refresh(service)

    # Schedule the ping job for the new service
    trigger = IntervalTrigger(seconds=5)
    scheduler.add_job(
        func=ping_service,
        kwargs={"service_id": service.id},
        trigger=trigger,
        replace_existing=True,
        id=str(service.id),
    )

    db.session.commit()
    return redirect(url_for("service_detail", id=service.id))
