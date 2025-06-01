import time
from datetime import datetime

from flask import (
    Blueprint,
    Response,
    abort,
    current_app,
    redirect,
    render_template,
    stream_with_context,
    url_for,
)
from flask_login import current_user, login_required

from downtime_panda.blueprints.service.forms import ServiceForm
from downtime_panda.extensions import db

from .models import Ping, Service

service_blueprint = Blueprint("service", __name__, template_folder="templates")


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
@login_required
def service_create():
    form = ServiceForm()
    if not form.validate_on_submit():
        # Render the service creation form with validation errors
        return render_template("create.html.jinja", form=form)

    # This tricks the user into thinking the service is created
    # even if it already exists.
    #
    # Sorry user :(
    service = Service.create_if_not_exists(
        name=form.name.data,
        uri=form.uri.data,
    )
    current_user.subscribe_to_service(service)

    return redirect(url_for(".service_detail", id=service.id))
