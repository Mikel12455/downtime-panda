from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from downtime_panda.blueprints.service.models import Service
from downtime_panda.blueprints.subscription.forms import SubscriptionForm
from downtime_panda.blueprints.subscription.messages import (
    SUBSCRIPTION_REGISTRATION_SUCCESSFUL,
)
from downtime_panda.blueprints.subscription.models import Subscription

subscription_blueprint = Blueprint(
    "subscription", __name__, template_folder="templates", static_folder="static"
)


@subscription_blueprint.route("/subscribe", methods=["GET", "POST"])
@login_required
def service_subscribe():
    form = SubscriptionForm()
    if not form.validate_on_submit():
        # Render the service creation form with validation errors
        return render_template(
            "blueprints/subscription/subscribe.html.jinja", form=form
        )

    # This tricks the user into thinking the service is created
    # even if it already exists.
    #
    # Sorry user :(
    service = Service.create_if_not_exists(
        uri=form.uri.data,
    )
    subscription = Subscription.subscribe_user_to_service(
        user=current_user,
        service=service,
        name=form.name.data,
    )

    flash(
        SUBSCRIPTION_REGISTRATION_SUCCESSFUL,
        "success",
    )
    return redirect(url_for(".view_subscription", uuid=subscription.uuid))


@subscription_blueprint.route("/", methods=["GET"])
@login_required
def list_subscriptions():
    """List all subscriptions for the current user."""
    subscriptions = Subscription.get_subscriptions_by_user(current_user)
    return render_template(
        "blueprints/subscription/list.html.jinja",
        subscriptions=subscriptions,
    )


@subscription_blueprint.route("/<uuid>", methods=["GET"])
@login_required
def view_subscription(uuid: str):
    """View the status of a subscribed service"""
    MAX_POINTS = 20
    subscription = Subscription.get_user_subscription_by_uuid(current_user, uuid)
    pings = subscription.service.get_latest_n_pings(MAX_POINTS)
    pings = list(reversed(pings))
    pings = {
        "x": [ping.pinged_at for ping in pings],
        "y": [ping.response_time.total_seconds() for ping in pings],
        "status": [ping.http_response for ping in pings],
        "type": "scatter",
    }
    return render_template(
        "blueprints/subscription/status.html.jinja",
        subscription=subscription,
        pings=pings,
        max_points=MAX_POINTS,
    )


@subscription_blueprint.route("/<uuid>/pings_since", methods=["GET"])
@login_required
def get_subscription_pings_since(uuid: str):
    """View the status of a subscribed service"""
    subscription = Subscription.get_user_subscription_by_uuid(current_user, uuid)

    since_date = datetime.fromisoformat(request.args["since"])
    pings = subscription.service.get_pings_since(since_date)
    pings = list(reversed(pings))
    pings = {
        "x": [ping.pinged_at for ping in pings],
        "y": [ping.response_time.total_seconds() for ping in pings],
        "status": [ping.http_response for ping in pings],
        "type": "scatter",
    }
    return pings
