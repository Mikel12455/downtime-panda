from typing import Literal

import pytest
from flask import Flask
from flask.testing import FlaskClient, FlaskCliRunner

from downtime_panda import create_app
from downtime_panda.blueprints.token.models import APIToken
from downtime_panda.blueprints.user.models import User
from downtime_panda.config import TestingConfig
from downtime_panda.extensions import db


@pytest.fixture()
def app():
    app = create_app(TestingConfig)
    with app.app_context():
        db.create_all()

    # other setup can go here

    yield app

    # clean up / reset resources here


@pytest.fixture()
def user_alice(app: Flask) -> User:
    with app.app_context():
        existing_user = User.register(
            username="alice",
            email="alice@mail.com",
            password="password",
        )

    return existing_user


@pytest.fixture()
def is_alice_logged_in(
    app: Flask, client: FlaskClient, user_alice: User
) -> Literal[True]:
    with app.app_context():
        db.session.add(user_alice)
        client.post(
            "/user/login",
            data={
                "email": user_alice.email,
                "password": "password",
            },
            follow_redirects=True,
        )

    return True


@pytest.fixture()
def user_bob(app: Flask) -> User:
    with app.app_context():
        existing_user = User.register(
            username="bob",
            email="bob@mail.com",
            password="password",
        )

    return existing_user


@pytest.fixture()
def is_bob_logged_in(app: Flask, client: FlaskClient, user_bob: User) -> Literal[True]:
    with app.app_context():
        db.session.add(user_bob)
        client.post(
            "/user/login",
            data={
                "email": user_bob.email,
                "password": "password",
            },
            follow_redirects=True,
        )

    return True


@pytest.fixture()
def client(app: Flask) -> FlaskClient:
    return app.test_client()


@pytest.fixture()
def runner(app: Flask) -> FlaskCliRunner:
    return app.test_cli_runner()


@pytest.fixture
def alice_token(client: FlaskClient, app: Flask, user_alice: User):
    with app.app_context():
        db.session.add(user_alice)
        token = APIToken.create_for_user(user_alice)

    return token
