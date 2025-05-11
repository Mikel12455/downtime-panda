import time

import requests
from flask import Flask, Response
from flask.templating import render_template

app = Flask(__name__)


@app.route("/")
def index() -> str:
    return render_template("index.html")


@app.route("/ping")
def ping():
    def pingStream():
        while True:
            time.sleep(5)
            response = requests.head("https://www.google.com")
            yield f"data: {response.status_code}\n\n"

    return Response(pingStream(), mimetype="text/event-stream")
