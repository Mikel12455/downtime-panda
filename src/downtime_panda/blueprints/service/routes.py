import time
from datetime import datetime
from http import HTTPStatus

from flask import (
    Blueprint,
    Response,
    abort,
    render_template,
    request,
    stream_with_context,
)
from loguru import logger

from downtime_panda.extensions import db

from .models import Ping, Service

service_blueprint = Blueprint("service", __name__)


# ------------------------------------ SSE ----------------------------------- #
def stream(service: Service, last_pinged_at: datetime):
    while True:
        logger.info("Test")
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
    return render_template("blueprints/service/detail.html.jinja", service=service)


@service_blueprint.route("/fetch/<int:id>")
def fetch_latest_pings(id):
    service = db.get_or_404(Service, id)
    latest_timestamp = request.form.get("latest_timestamp", None)
    if not latest_timestamp:
        abort(HTTPStatus.BAD_REQUEST, description="Missing latest_timestamp")

    latest_pings = db.session.scalars(
        service.ping.select()
        .order_by(Ping.pinged_at.desc())
        .filter_by(Ping.pinged_at > latest_timestamp)
    ).all()

    return {
        "latest_pings": [ping.dump_json() for ping in latest_pings],
    }


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
