from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from downtime_panda.blueprints.service.models import Service
from downtime_panda.blueprints.subscription.forms import SubscriptionForm
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
        return render_template("subscribe.html.jinja", form=form)

    # This tricks the user into thinking the service is created
    # even if it already exists.
    #
    # Sorry user :(
    service = Service.create_if_not_exists(
        uri=form.uri.data,
    )
    Subscription.subscribe_user_to_service(
        user=current_user,
        service=service,
    )

    flash(
        "You have successfully subscribed.",
        "success",
    )
    return redirect(url_for("home.index"))
