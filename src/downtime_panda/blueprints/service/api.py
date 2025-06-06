from flask import Blueprint, abort
from sqlalchemy import select

from downtime_panda.blueprints.service.models import Service
from downtime_panda.blueprints.subscription.models import Subscription
from downtime_panda.blueprints.user.models import User
from downtime_panda.extensions import db, token_auth

service_api_blueprint = Blueprint("service_api", __name__)


@service_api_blueprint.get("/heartbeat")
@token_auth.login_required
def heartbeat():
    """
    Endpoint to check if the service API is running.
    """
    return {"status": "ok"}


@service_api_blueprint.get("<subscription_uuid>/status")
@token_auth.login_required
def subscription_status(subscription_uuid: str):
    """
    Endpoint to check the status of a subscription.

    Args:
        subscription_uuid (str): The UUID of the subscription.

    Returns:
        dict: A dictionary containing the status of the subscription.
    """
    user: User = token_auth.current_user()
    if not user:
        abort(401)

    query = (
        select(Service)
        .join(User.services)
        .where(User.id == user.id, Subscription.uuid == subscription_uuid)
    )
    service = db.session.execute(query).scalar_one_or_none()
    if not service:
        abort(404, description="Subscription not found or does not belong to the user.")

    latest_ping = service.get_latest_ping()
    if not latest_ping:
        abort(404, description="No pings found for the service.")

    return latest_ping.to_dict()
