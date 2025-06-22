"""
User management routes for Downtime Panda.

This module handles user registration, login, logout, profile management,
and API token management.
"""

import flask_login
from flask import Blueprint, flash, redirect, render_template, url_for

from downtime_panda.blueprints.user.forms import (
    LoginForm,
    RegisterForm,
)
from downtime_panda.blueprints.user.messages import (
    ERROR_INVALID_CREDENTIALS,
    SUCCESS_LOGIN,
    SUCCESS_LOGOUT,
    SUCCESS_REGISTRATION,
)
from downtime_panda.extensions import login_manager

from .models import User

# ---------------------------------------------------------------------------- #
#                                AUTHENTICATION                                #
# ---------------------------------------------------------------------------- #

auth_blueprint = Blueprint("auth", __name__)


@login_manager.user_loader
def user_loader(id: str):
    id = int(id)
    return User.get_by_id(id)


@auth_blueprint.route("/register", methods=["GET", "POST"])
def register():
    """Register a new user."""
    form = RegisterForm()
    if not form.validate_on_submit():
        return render_template("blueprints/user/register.html.jinja", form=form)

    try:
        User.register(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data,
        )
    except ValueError as e:
        flash("Error: " + str(e), "error")
        return render_template(
            "blueprints/user/register.html.jinja", form=form, error=str(e)
        )

    user = User.get_by_email(form.email.data)
    flask_login.login_user(user)

    flash(SUCCESS_REGISTRATION, "success")
    return redirect(url_for("home.index"))


@auth_blueprint.route("/login", methods=["GET", "POST"])
def login():
    """Log in an existing user."""
    form = LoginForm()
    if not form.validate_on_submit():
        return render_template("blueprints/user/login.html.jinja", form=form)

    user = User.get_by_email(form.email.data)
    if user and user.verify_password(form.password.data):
        flask_login.login_user(user, remember=form.remember_me.data)
        flash(SUCCESS_LOGIN, "success")
        return redirect(url_for("home.index"))

    flash(ERROR_INVALID_CREDENTIALS, "danger")
    return render_template("blueprints/user/login.html.jinja", form=form)


@auth_blueprint.route("/logout", methods=["POST"])
def logout():
    """Log out the current user."""
    if flask_login.current_user.is_authenticated:
        flask_login.logout_user()
        flash(SUCCESS_LOGOUT, "success")
    return redirect(url_for("home.index"))


# ---------------------------------------------------------------------------- #
#                                    PROFILE                                   #
# ---------------------------------------------------------------------------- #


user_blueprint = Blueprint("user", __name__)


@user_blueprint.route("/profile")
@flask_login.login_required
def show_profile():
    """Display the user's profile."""
    return render_template("blueprints/user/profile.html.jinja")
