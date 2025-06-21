from flask import Blueprint, render_template

home_blueprint = Blueprint("home", __name__)


@home_blueprint.route("/")
def index() -> str:
    """Render the home page."""
    return render_template("blueprints/index.html.jinja")
