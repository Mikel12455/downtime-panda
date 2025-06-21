from datetime import datetime, timedelta
from http import HTTPStatus

import pytest
from flask import Flask, url_for
from flask.testing import FlaskClient
from loguru import logger

from downtime_panda.blueprints.service.models import Ping, Service
from downtime_panda.blueprints.subscription.models import Subscription
from downtime_panda.blueprints.token.models import APIToken
from downtime_panda.blueprints.user.models import User
from downtime_panda.extensions import db


@pytest.fixture
def service(app: Flask):
    with app.app_context():
        service = Service("https://random.nonexistent.service")
        db.session.add(service)
        db.session.commit()

    return service


@pytest.fixture()
def ping_for_service(app: Flask, service: Service):
    with app.app_context():
        db.session.add(service)

        pinged_at = datetime(2025, 6, 9, 0, 0, 0)
        response_time = timedelta(seconds=1)
        ping = Ping(
            service_id=service.id,
            http_status=HTTPStatus.OK,
            response_time=response_time,
            pinged_at=pinged_at,
        )
        service.ping.add(ping)

        db.session.commit()

    return ping


@pytest.fixture()
def alice_subscription(app: Flask, service: Service, user_alice: User):
    with app.app_context():
        db.session.add(user_alice)
        db.session.add(service)

        subscription = Subscription.subscribe_user_to_service(
            user_alice,
            service,
            "A Random Nonexistent Service",
        )

    return subscription


def test_api_with_token(
    app: Flask,
    client: FlaskClient,
    alice_token: APIToken,
    alice_subscription: Subscription,
    ping_for_service: Ping,
):
    """Tests the "happy path" of the api: Request with correct token that returns the latest ping."""
    with app.test_request_context():
        db.session.add(alice_token)
        db.session.add(alice_subscription)
        db.session.add(ping_for_service)

        assert alice_token.exists()

        response = client.get(
            url_for(
                "subscription_api.get_status", subscription_uuid=alice_subscription.uuid
            ),
            headers={"Authorization": f"Bearer {alice_token.token}"},
        )

        assert response.status_code == HTTPStatus.OK

        logger.info(response.data)

        assert f'"http_response": {ping_for_service.http_response}' in response.text
        assert (
            f'"pinged_at": "{ping_for_service.pinged_at.isoformat()}"' in response.text
        )


def test_api_unauthorized_access(
    app: Flask,
    client: FlaskClient,
    alice_subscription: Subscription,
):
    with app.test_request_context():
        db.session.add(alice_subscription)

        response = client.get(
            url_for(
                "subscription_api.get_status", subscription_uuid=alice_subscription.uuid
            )
        )

        assert response.status_code == HTTPStatus.UNAUTHORIZED


def test_api_nonexistent_subscription(
    app: Flask,
    client: FlaskClient,
    alice_token: APIToken,
):
    with app.test_request_context():
        db.session.add(alice_token)

        response = client.get(
            url_for(
                "subscription_api.get_status",
                subscription_uuid="00000000-0000-0000-0000-000000000000",
            ),
            headers={"Authorization": f"Bearer {alice_token.token}"},
        )

        assert response.status_code == HTTPStatus.NOT_FOUND
