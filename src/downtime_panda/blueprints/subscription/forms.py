from flask_wtf import FlaskForm
from wtforms import URLField
from wtforms.validators import URL, DataRequired


class SubscriptionForm(FlaskForm):
    uri = URLField(
        "URI",
        description="URI of the service",
        validators=[DataRequired("Service URI is required"), URL("Invalid URI format")],
    )
