import base64
import os
import time
from datetime import datetime

import flask_login
import pytz
import requests
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from flask import Flask, Response, abort, flash, redirect, request, url_for
from flask.templating import render_template
from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError

from downtime_panda import model

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("DTPANDA_SECRET_KEY")

login_manager = flask_login.LoginManager()
login_manager.init_app(app)


def b64encode(data: str):
    return base64.b64encode(data.encode()).decode()


app.jinja_env.filters["b64encode"] = b64encode

DEBUG = os.getenv("DTPANDA_DEBUG", "false").lower() in ("true", "1", "yes")
app.config["DEBUG"] = DEBUG

DB_DIALECT = os.getenv("DTPANDA_DB_DIALECT")
DB_HOST = os.getenv("DTPANDA_DB_HOST")
DB_PORT = os.getenv("DTPANDA_DB_PORT")
DB_USER = os.getenv("DTPANDA_DB_USER")
DB_PASSWORD = os.getenv("DTPANDA_DB_PASSWORD")
DB_DATABASE = os.getenv("DTPANDA_DB_DATABASE")

app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"{DB_DIALECT}://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_DATABASE}"
)
model.db.init_app(app)

with app.app_context():
    model.db.create_all()

jobstore = SQLAlchemyJobStore(
    url=app.config["SQLALCHEMY_DATABASE_URI"], tableschema="downtime_panda"
)

if not (app.debug or DEBUG) or os.environ.get("WERKZEUG_RUN_MAIN") == "true":
    scheduler = BackgroundScheduler()
    scheduler.add_jobstore(jobstore)
    scheduler.timezone = pytz.utc
    scheduler.start()


def ping_service(service_id: int) -> None:
    with app.app_context():
        service = model.db.session.get(model.Service, service_id)
        app.logger.info(service)

        pinged_at = datetime.now(pytz.utc)
        response = requests.head(service.uri)
        ping = model.Ping(
            service_id=service.id,
            http_status=response.status_code,
            pinged_at=pinged_at,
        )
        service.ping.add(ping)
        model.db.session.commit()


# ---------------------------------------------------------------------------- #
#                                     HOME                                     #
# ---------------------------------------------------------------------------- #


@app.route("/")
def index() -> str:
    return render_template("index.html.jinja")


# ---------------------------------------------------------------------------- #
#                                    SERVICE                                   #
# ---------------------------------------------------------------------------- #


@app.route("/service/<int:id>")
def service_detail(id):
    service = model.db.get_or_404(model.Service, id)
    return render_template("service_detail.html.jinja", service=service)


@app.route("/service/stream/<int:id>")
def service_stream(id):
    service = model.db.get_or_404(model.Service, id)

    last_ping = model.db.session.scalars(service.ping.select()).first()

    if not last_ping:
        abort(404)

    last_pinged_at = last_ping.pinged_at

    def stream(service: model.Service, last_pinged_at: datetime):
        with app.app_context():
            while True:
                new_pings = model.db.session.scalars(
                    service.ping.select()
                    .where(model.Ping.pinged_at > last_pinged_at)
                    .order_by(model.Ping.pinged_at.desc())
                ).all()

                if new_pings:
                    last_pinged_at = max(new_pings, key=lambda x: x.pinged_at).pinged_at
                    yield f"data: {new_pings[0].dump_json()}\n\n"

                time.sleep(1)

    return Response(stream(service, last_pinged_at), mimetype="text/event-stream")


@app.route("/service/create", methods=["GET", "POST"])
def service_create():
    if request.method == "POST":
        # Insert a new service into the database
        service = model.Service(
            name=request.form["name"],
            uri=request.form["uri"],
        )
        model.db.session.add(service)
        model.db.session.flush((service,))
        model.db.session.refresh(service)

        # Schedule the ping job for the new service
        trigger = IntervalTrigger(seconds=5)
        scheduler.add_job(
            func=ping_service,
            kwargs={"service_id": service.id},
            trigger=trigger,
            replace_existing=True,
            id=str(service.id),
        )

        model.db.session.commit()
        return redirect(url_for("service_detail", id=service.id))

    return render_template("service_create.html.jinja")


# ---------------------------------------------------------------------------- #
#                                     USER                                     #
# ---------------------------------------------------------------------------- #


@login_manager.user_loader
def user_loader(id: str):
    id = int(id)
    return model.User.get_by_id(id)


@app.route("/register", methods=["GET", "POST"])
def register():
    def username_is_free(form, field):
        if model.User.username_exists(field.data):
            raise ValidationError("Username already exists.")

    def email_is_free(form, field):
        if model.User.email_exists(field.data):
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
        model.User.add_user(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data,
        )
    except ValueError as e:
        flash("Error: " + str(e), "error")
        return render_template("register.html.jinja", form=form, error=str(e))

    return redirect(url_for("index"))


@app.route("/login", methods=["GET", "POST"])
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

    user = model.User.get_by_email(form.email.data)
    if user and user.verify_password(form.password.data):
        flask_login.login_user(user)
        return redirect(url_for("index"))

    return render_template("login.html.jinja", form=form, error="Invalid credentials")


@app.route("/logout")
def logout():
    flask_login.logout_user()
    return redirect(url_for("index"))


@app.route("/user")
def user_index():
    return render_template("user_index.html.jinja")


@app.route("/stream/ping/<website>")
def ping(website: str):
    def pingStream(website: str):
        while True:
            response = requests.head(website)
            yield f"data: {response.status_code}\n\n"
            time.sleep(5)

    try:
        website = base64.urlsafe_b64decode(website.encode()).decode()
    except Exception:
        return Response("Invalid base64 encoding", status=400)
    if not (website.startswith("http://") or website.startswith("https://")):
        website = f"https://{website}"

    return Response(pingStream(website), mimetype="text/event-stream")
