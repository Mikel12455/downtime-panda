from http import HTTPStatus

import flask_login
from flask import Flask
from flask.testing import FlaskClient
from flask_login import current_user

from downtime_panda.blueprints.user.messages import (
    ERROR_EMAIL_TAKEN,
    ERROR_INVALID_CREDENTIALS,
    ERROR_PASSWORD_MISMATCH,
    ERROR_USERNAME_TAKEN,
)
from downtime_panda.blueprints.user.models import User
from downtime_panda.extensions import db

# ---------------------------------------------------------------------------- #
#                                 REGISTRATION                                 #
# ---------------------------------------------------------------------------- #


def test_user_registration(client: FlaskClient, app: Flask):
    USERNAME = "new_user"
    USER_EMAIL = "new_user@mail.com"
    with app.test_request_context():
        response = client.post(
            "/user/register",
            data={
                "username": USERNAME,
                "email": USER_EMAIL,
                "password": "testpassword",
                "confirm_password": "testpassword",
            },
            follow_redirects=True,
        )

        assert response.status_code == HTTPStatus.OK
        assert current_user.is_authenticated

        user = User.get_by_email(USER_EMAIL)
        assert user is not None
        assert user.username == USERNAME


def test_username_already_exists(client: FlaskClient, app: Flask, user_alice: User):
    with app.test_request_context():
        db.session.add(user_alice)

        response = client.post(
            "/user/register",
            data={
                "username": user_alice.username,
                "email": "new_user@mail.com",
                "password": "testpassword",
                "confirm_password": "testpassword",
            },
            follow_redirects=True,
        )

        assert response.status_code == HTTPStatus.OK
        assert ERROR_USERNAME_TAKEN.encode() in response.data


def test_email_already_exists(client: FlaskClient, app: Flask, user_alice: User):
    with app.test_request_context():
        db.session.add(user_alice)

        response = client.post(
            "/user/register",
            data={
                "username": "new_user",
                "email": user_alice.email,
                "password": "testpassword",
                "confirm_password": "testpassword",
            },
            follow_redirects=True,
        )

        assert response.status_code == HTTPStatus.OK
        assert ERROR_EMAIL_TAKEN.encode() in response.data


def test_confirm_password_mismatch(client: FlaskClient, app: Flask):
    with app.test_request_context():
        response = client.post(
            "/user/register",
            data={
                "username": "user",
                "email": "user@mail.com",
                "password": "testpassword",
                "confirm_password": "mismatchpassword",
            },
            follow_redirects=True,
        )

        assert response.status_code == HTTPStatus.OK
        assert ERROR_PASSWORD_MISMATCH.encode() in response.data


# ---------------------------------------------------------------------------- #
#                                     LOGIN                                    #
# ---------------------------------------------------------------------------- #


def test_user_login(client: FlaskClient, app: Flask, user_alice: User):
    with app.test_request_context():
        db.session.add(user_alice)

        response = client.post(
            "/user/login",
            data={
                "email": user_alice.email,
                "password": "password",
            },
            follow_redirects=True,
        )

        assert response.status_code == HTTPStatus.OK
        assert current_user.is_authenticated
        assert current_user.username == user_alice.username


def test_invalid_email_login(client: FlaskClient, app: Flask, user_alice: User):
    with app.test_request_context():
        db.session.add(user_alice)

        response = client.post(
            "/user/login",
            data={
                "email": "invalid_email@mail.com",
                "password": "password",
            },
            follow_redirects=True,
        )

        assert response.status_code == HTTPStatus.OK
        assert not current_user.is_authenticated
        assert ERROR_INVALID_CREDENTIALS.encode() in response.data


def test_invalid_password_login(client: FlaskClient, app: Flask, user_alice: User):
    with app.test_request_context():
        db.session.add(user_alice)

        response = client.post(
            "/user/login",
            data={
                "email": user_alice.email,
                "password": "wrongpassword",
            },
            follow_redirects=True,
        )

        assert response.status_code == HTTPStatus.OK
        assert not current_user.is_authenticated
        assert ERROR_INVALID_CREDENTIALS.encode() in response.data


# ---------------------------------------------------------------------------- #
#                                    LOGOUT                                    #
# ---------------------------------------------------------------------------- #


def test_user_logout(client: FlaskClient, app: Flask, user_alice: User):
    with app.test_request_context():
        db.session.add(user_alice)
        flask_login.login_user(user_alice)
        assert current_user.is_authenticated

        response = client.get("/user/logout", follow_redirects=True)

        assert response.status_code == HTTPStatus.OK
        assert not current_user.is_authenticated
