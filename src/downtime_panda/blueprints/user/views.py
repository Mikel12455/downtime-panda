import flask_login
from flask import Blueprint, flash, redirect, render_template, url_for
from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, ValidationError
from wtforms.validators import DataRequired, Email, EqualTo

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
    def username_is_free(form, field):
        if User.username_exists(field.data):
            raise ValidationError("Username already exists.")

    def email_is_free(form, field):
        if User.email_exists(field.data):
            raise ValidationError("Email already exists.")

    class RegisterForm(FlaskForm):
        username = StringField(
            "Username",
            description="Username",
            validators=[DataRequired("Username is required"), username_is_free],
        )
        email = StringField(
            "Email",
            description="Email",
            validators=[DataRequired("Email is required"), Email(), email_is_free],
        )
        password = PasswordField(
            "Password",
            description="Password",
            validators=[
                DataRequired("Password is required"),
            ],
        )
        confirm_password = PasswordField(
            "Confirm Password",
            description="Confirm password",
            validators=[EqualTo("password", message="Passwords must match")],
        )

    form = RegisterForm()
    if not form.validate_on_submit():
        return render_template("register.html.jinja", form=form)

    try:
        User.add_user(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data,
        )
    except ValueError as e:
        flash("Error: " + str(e), "error")
        return render_template("register.html.jinja", form=form, error=str(e))

    return redirect(url_for("home.index"))


# ---------------------------------------------------------------------------- #
#                                     LOGIN                                    #
# ---------------------------------------------------------------------------- #
@user_blueprint.route("/login", methods=["GET", "POST"])
def login():
    class LoginForm(FlaskForm):
        email = StringField(
            "Email",
            description="Email",
            validators=[DataRequired("Email is required"), Email()],
        )
        password = PasswordField(
            "Password",
            description="Password",
            validators=[DataRequired("Password is required")],
        )

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
