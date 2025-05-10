import requests
from flask import Flask
from flask.templating import render_template

app = Flask(__name__)


@app.route("/")
def index() -> str:
    r = requests.head("https://www.google.com")
    return render_template("index.html", response=r)


def main() -> None:
    app.run()
