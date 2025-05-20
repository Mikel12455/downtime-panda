import base64
import os
import time

import requests
from flask import Flask, Response, redirect, request, url_for
from flask.templating import render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)


class Service(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    uri: Mapped[str] = mapped_column()


app = Flask(__name__)


def b64encode(data: str):
    return base64.b64encode(data.encode()).decode()


app.jinja_env.filters["b64encode"] = b64encode


DB_DIALECT = os.getenv("DTPANDA_DB_DIALECT")
DB_HOST = os.getenv("DTPANDA_DB_HOST")
DB_PORT = os.getenv("DTPANDA_DB_PORT")
DB_USER = os.getenv("DTPANDA_DB_USER")
DB_PASSWORD = os.getenv("DTPANDA_DB_PASSWORD")
DB_DATABASE = os.getenv("DTPANDA_DB_DATABASE")

app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"{DB_DIALECT}://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_DATABASE}"
)
db.init_app(app)

with app.app_context():
    db.create_all()


# ----------------------------------- HOME ----------------------------------- #
@app.route("/")
def index() -> str:
    return render_template("index.html.jinja")


# ---------------------------------- SERVICE --------------------------------- #
@app.route("/service/create", methods=["GET", "POST"])
def service_create():
    if request.method == "POST":
        service = Service(
            name=request.form["name"],
            uri=request.form["uri"],
        )
        db.session.add(service)
        db.session.commit()
        return redirect(url_for("service_detail", id=service.id))

    return render_template("service_create.html.jinja")


@app.route("/service/<int:id>")
def service_detail(id):
    service = db.get_or_404(Service, id)
    return render_template("service_detail.html.jinja", service=service)


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
