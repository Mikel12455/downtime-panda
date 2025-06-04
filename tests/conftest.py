import pytest
from flask import Flask

from downtime_panda import create_app
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
def existing_user(app: Flask):
    from downtime_panda.blueprints.user.models import User

    with app.app_context():
        existing_user = User.register(
            username="existing_user",
            email="existing_user@mail.com",
            password="password",
        )

    return existing_user


@pytest.fixture()
def client(app: Flask):
    return app.test_client()


@pytest.fixture()
def runner(app: Flask):
    return app.test_cli_runner()
