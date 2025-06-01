from flask_wtf import FlaskForm
from wtforms import StringField, URLField
from wtforms.validators import DataRequired


class ServiceForm(FlaskForm):
    name = StringField(
        "Service Name",
        description="Name of the service",
        validators=[DataRequired("Service name is required")],
    )
    uri = URLField(
        "URI",
        description="URI of the service",
        validators=[DataRequired("Service URI is required")],
    )
