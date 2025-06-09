from http import HTTPStatus

import pytest
from flask import Flask, url_for
from flask.testing import FlaskClient

from downtime_panda.blueprints.token.messages import ERROR_TOKEN_DOESNT_EXIST
from downtime_panda.blueprints.token.models import APIToken
from downtime_panda.blueprints.user.models import User
from downtime_panda.extensions import db


@pytest.fixture
def alice_token(client: FlaskClient, app: Flask, user_alice: User):
    with app.app_context():
        db.session.add(user_alice)
        token = APIToken.create_for_user(user_alice)

    return token


def test_generate_new_token(client: FlaskClient, app: Flask, is_alice_logged_in: True):
    """Tests the generation of a token for a user (Alice, in this case)"""
    with app.test_request_context():
        response = client.post(url_for("token.generate_token"), follow_redirects=True)

    assert response.status_code == HTTPStatus.OK


def test_revoke_token(
    client: FlaskClient,
    app: Flask,
    is_alice_logged_in: True,
    alice_token: APIToken,
):
    """Tests the token revokation from a legitimate user (Alice, in this case)."""
    with app.test_request_context():
        db.session.add(alice_token)
        assert alice_token.exists()

        response = client.post(
            url_for("token.revoke_token", token_id=alice_token.id),
            follow_redirects=True,
        )

        assert response.status_code == HTTPStatus.OK
        assert not alice_token.exists()


def test_revoke_nonesistent_token(
    app: Flask,
    client: FlaskClient,
    is_alice_logged_in: True,
    alice_token: APIToken,
):
    """Tests the token revokation from a legitimate user (Alice, in this case), but for a token that doesn't exist."""
    with app.test_request_context():
        db.session.add(alice_token)
        assert alice_token.exists()

        response = client.post(
            url_for("token.revoke_token", token_id=-1),
            follow_redirects=True,
        )

        assert response.status_code == HTTPStatus.NOT_FOUND
        assert ERROR_TOKEN_DOESNT_EXIST.encode() in response.data
        assert alice_token.exists()


def test_token_revoke_from_unauthorized_user(
    client: FlaskClient, app: Flask, is_bob_logged_in: True, alice_token: APIToken
):
    """Tests whether a user can revoke the token of another user."""
    with app.test_request_context():
        db.session.add(alice_token)
        assert alice_token.exists()

        response = client.post(
            url_for("token.revoke_token", token_id=alice_token.id),
            follow_redirects=True,
        )

        assert response.status_code == HTTPStatus.NOT_FOUND
        assert ERROR_TOKEN_DOESNT_EXIST.encode() in response.data
        assert alice_token.exists()
