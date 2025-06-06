from flask_wtf import FlaskForm
from wtforms import StringField, URLField
from wtforms.validators import URL, InputRequired, Length


class SubscriptionForm(FlaskForm):
    name = StringField(
        "Name",
        description="Name of the service",
        validators=[
            InputRequired("Service name is required"),
            Length(
                min=1,
                max=255,
                message="Service name must be between 1 and 255 characters",
            ),
        ],
    )
    uri = URLField(
        "URI",
        description="URI of the service",
        validators=[
            InputRequired("Service URI is required"),
            URL("Invalid URI format"),
            Length(max=255, message="Service URI must be less than 255 characters"),
        ],
    )
