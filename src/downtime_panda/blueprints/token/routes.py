from http import HTTPStatus

import flask_login
from flask import Blueprint, flash, redirect, render_template, url_for

from downtime_panda.blueprints.token.messages import (
    ERROR_TOKEN_DOESNT_EXIST,
    SUCCESS_TOKEN_CREATED,
    SUCCESS_TOKEN_REVOKED,
)
from downtime_panda.blueprints.token.models import APIToken

token_blueprint = Blueprint("token", __name__)


@token_blueprint.get("/")
@flask_login.login_required
def list_tokens():
    """Display the user's API tokens."""

    return render_template("blueprints/token/list.html.jinja")


@token_blueprint.post("/generate")
@flask_login.login_required
def generate_token():
    """Create a new API token for the user."""

    APIToken.create_for_user(flask_login.current_user)
    flash(SUCCESS_TOKEN_CREATED, "success")
    return redirect(url_for(".list_tokens"))


@token_blueprint.post("/revoke/<int:token_id>")
@flask_login.login_required
def revoke_token(token_id: int):
    """Delete an API token."""

    token = APIToken.find_by_id(token_id=token_id, user=flask_login.current_user)
    if not token:
        flash(ERROR_TOKEN_DOESNT_EXIST, "danger")
        return redirect(url_for(".list_tokens"), code=HTTPStatus.NOT_FOUND)

    token.revoke()
    flash(SUCCESS_TOKEN_REVOKED, "success")
    return redirect(url_for(".list_tokens"))
