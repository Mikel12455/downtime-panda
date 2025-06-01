from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, ValidationError
from wtforms.validators import DataRequired, Email, EqualTo

from downtime_panda.blueprints.user.models import User


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
