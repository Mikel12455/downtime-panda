from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, ValidationError
from wtforms.validators import DataRequired, Email, EqualTo, Length

from downtime_panda.blueprints.user.messages import (
    ERROR_EMAIL_NOT_VALID,
    ERROR_EMAIL_REQUIRED,
    ERROR_EMAIL_TAKEN,
    ERROR_PASSWORD_MISMATCH,
    ERROR_PASSWORD_REQUIRED,
    ERROR_PASSWORD_TOO_SHORT,
    ERROR_USERNAME_REQUIRED,
    ERROR_USERNAME_TAKEN,
)
from downtime_panda.blueprints.user.models import User


class LoginForm(FlaskForm):
    email = StringField(
        "Email",
        description="Email",
        validators=[DataRequired(ERROR_EMAIL_REQUIRED), Email(ERROR_EMAIL_NOT_VALID)],
    )
    password = PasswordField(
        "Password",
        description="Password",
        validators=[
            DataRequired(ERROR_PASSWORD_REQUIRED),
        ],
    )


def username_is_free(form, field):
    if User.username_exists(field.data):
        raise ValidationError(ERROR_USERNAME_TAKEN)


def email_is_free(form, field):
    if User.email_exists(field.data):
        raise ValidationError(ERROR_EMAIL_TAKEN)


class RegisterForm(FlaskForm):
    username = StringField(
        "Username",
        description="Username",
        validators=[DataRequired(ERROR_USERNAME_REQUIRED), username_is_free],
    )
    email = StringField(
        "Email",
        description="Email",
        validators=[
            DataRequired(ERROR_EMAIL_REQUIRED),
            Email(ERROR_EMAIL_NOT_VALID),
            email_is_free,
        ],
    )
    password = PasswordField(
        "Password",
        description="Password",
        validators=[
            DataRequired(ERROR_PASSWORD_REQUIRED),
            Length(min=8, message=ERROR_PASSWORD_TOO_SHORT),
        ],
    )
    confirm_password = PasswordField(
        "Confirm Password",
        description="Confirm password",
        validators=[
            DataRequired(ERROR_PASSWORD_REQUIRED),
            Length(min=8, message=ERROR_PASSWORD_TOO_SHORT),
            EqualTo("password", message=ERROR_PASSWORD_MISMATCH),
        ],
    )
