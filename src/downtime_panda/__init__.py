from flask import Flask
from flask.templating import render_template

app = Flask(__name__)

@app.route("/")
def index() -> str:
    return render_template("index.html")
    
def main() -> None:
    app.run()