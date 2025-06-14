from http import HTTPStatus

from flask import Blueprint, abort, request

from downtime_panda.blueprints.subscription.models import Subscription
from downtime_panda.blueprints.user.models import User
from downtime_panda.extensions import token_auth

subscription_api_blueprint = Blueprint("subscription_api", __name__)


@subscription_api_blueprint.get("/heartbeat")
def heartbeat():
    """
    Endpoint to check if the service API is running.
    """
    return {"status": "ok"}


@subscription_api_blueprint.get("/status")
@token_auth.login_required
def get_status():
    """
    Endpoint to check the status of a subscription.

    Returns:
        dict: A dictionary containing the status of the subscription.
    """
    user: User | None = token_auth.current_user()
    if not user:
        abort(HTTPStatus.UNAUTHORIZED)

    subscription_uuid = request.args.get("subscription_uuid")

    subscription = Subscription.get_user_subscription_by_uuid(user, subscription_uuid)
    if not subscription:
        abort(
            HTTPStatus.NOT_FOUND,
            description="Subscription not found.",
        )

    latest_ping = subscription.service.get_latest_ping()
    if not latest_ping:
        abort(HTTPStatus.NOT_FOUND, description="No pings found for the service.")

    return latest_ping.to_dict()
