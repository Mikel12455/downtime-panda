import flask_login
from flask import Blueprint, flash, redirect, render_template, url_for

from downtime_panda.blueprints.user.forms import (
    LoginForm,
    RegisterForm,
)
from downtime_panda.extensions import login_manager

from .models import User

user_blueprint = Blueprint(
    "user", __name__, static_folder="static", template_folder="templates"
)


@login_manager.user_loader
def user_loader(id: str):
    id = int(id)
    return User.get_by_id(id)


# ---------------------------------------------------------------------------- #
#                                 REGISTRATION                                 #
# ---------------------------------------------------------------------------- #
@user_blueprint.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if not form.validate_on_submit():
        return render_template("register.html.jinja", form=form)

    try:
        User.register(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data,
        )
    except ValueError as e:
        flash("Error: " + str(e), "error")
        return render_template("register.html.jinja", form=form, error=str(e))

    user = User.get_by_email(form.email.data)
    flask_login.login_user(user)

    return redirect(url_for("home.index"))


# ---------------------------------------------------------------------------- #
#                                     LOGIN                                    #
# ---------------------------------------------------------------------------- #
@user_blueprint.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if not form.validate_on_submit():
        # GET
        return render_template("login.html.jinja", form=form)

    user = User.get_by_email(form.email.data)
    if user and user.verify_password(form.password.data):
        flask_login.login_user(user)
        return redirect(url_for("home.index"))

    return render_template("login.html.jinja", form=form, error="Invalid credentials")


# ---------------------------------------------------------------------------- #
#                                    LOGOUT                                    #
# ---------------------------------------------------------------------------- #
@user_blueprint.route("/logout")
def logout():
    flask_login.logout_user()
    return redirect(url_for("home.index"))


# ---------------------------------------------------------------------------- #
#                                    PROFILE                                   #
# ---------------------------------------------------------------------------- #
@user_blueprint.route("/profile")
@flask_login.login_required
def profile():
    return render_template("profile.html.jinja")
