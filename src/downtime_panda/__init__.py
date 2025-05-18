import time

import requests
from flask import Flask, Response
from flask.templating import render_template

app = Flask(__name__)


# ----------------------------------- HOME ----------------------------------- #
@app.route("/")
def index() -> str:
    return render_template("index.html.jinja")


@app.route("/stream/ping/<website>")
def ping(website: str):
    def pingStream(website: str):
        while True:
            response = requests.head(website)
            yield f"data: {response.status_code}\n\n"
            time.sleep(5)

    if not (website.startswith("http://") or website.startswith("https://")):
        website = f"https://{website}"

    return Response(pingStream(website), mimetype="text/event-stream")
