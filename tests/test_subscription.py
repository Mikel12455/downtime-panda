from http import HTTPStatus
from typing import Literal

import pytest
from flask import Flask, url_for
from flask.testing import FlaskClient
from sqlalchemy import exists

from downtime_panda.blueprints.service.models import Service
from downtime_panda.blueprints.subscription.messages import (
    SUBSCRIPTION_REGISTRATION_SUCCESSFUL,
)
from downtime_panda.blueprints.subscription.models import Subscription
from downtime_panda.blueprints.user.models import User
from downtime_panda.extensions import db


@pytest.fixture()
def existing_service(app: Flask):
    """Represents a service, saved in the app"""
    with app.app_context():
        service = Service("https://random.nonexistent.service")
        db.session.add(service)
        db.session.commit()

    return service


def test_subscribing_to_new_service(
    app: Flask,
    client: FlaskClient,
    user_alice: User,
    is_alice_logged_in: Literal[True],
):
    """Tests subscribing to a service that doesn't exists yet in the db"""
    URI = "https://a.new.service"
    SUB_NAME = "A New Service"

    with app.app_context():
        assert not db.session.query(exists().where(Service.uri == URI)).scalar()
        db.session.add(user_alice)

    with app.test_request_context():
        response = client.post(
            url_for(
                "subscription.service_subscribe",
            ),
            data={
                "uri": URI,
                "name": SUB_NAME,
            },
            follow_redirects=True,
        )

        assert response.status_code == HTTPStatus.OK
        assert SUBSCRIPTION_REGISTRATION_SUCCESSFUL.encode() in response.data
        assert SUB_NAME.encode() in response.data

        assert db.session.query(exists().where(Service.uri == URI)).scalar()

        assert db.session.query(
            exists().where(
                Subscription.service_id == Service.id,
                Subscription.user_id == user_alice.id,
            )
        ).scalar()


def test_subscribing_to_existing_service(
    app: Flask,
    client: FlaskClient,
    user_alice: User,
    is_alice_logged_in: Literal[True],
    existing_service: Service,
):
    """Tests subscribing to a service that already exists in the db"""
    SUB_NAME = "An Existing Service"

    with app.app_context():
        db.session.add(user_alice)
        db.session.add(existing_service)

        assert db.session.query(
            exists().where(Service.uri == existing_service.uri)
        ).scalar()

    with app.test_request_context():
        response = client.post(
            url_for(
                "subscription.service_subscribe",
            ),
            data={
                "uri": existing_service.uri,
                "name": SUB_NAME,
            },
            follow_redirects=True,
        )

        assert response.status_code == HTTPStatus.OK
        assert SUBSCRIPTION_REGISTRATION_SUCCESSFUL.encode() in response.data
        assert SUB_NAME.encode() in response.data

        assert db.session.query(
            exists().where(
                Subscription.service_id == Service.id,
                Subscription.user_id == user_alice.id,
            )
        ).scalar()
