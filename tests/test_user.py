from flask import Flask
from flask.testing import FlaskClient

from downtime_panda.blueprints.user.models import User


def test_user_registration(client: FlaskClient, app: Flask):
    USER_EMAIL = "user@mail.com"
    with app.test_request_context():
        response = client.post(
            "/user/register",
            data={
                "username": "user",
                "email": USER_EMAIL,
                "password": "testpassword",
                "confirm_password": "testpassword",
            },
            follow_redirects=True,
        )
        print(response.data)
        assert response.status_code == 200
        user = User.get_by_email(USER_EMAIL)

        assert user is not None
        assert user.username == "user"
