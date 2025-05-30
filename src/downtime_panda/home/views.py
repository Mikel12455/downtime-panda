from flask import Blueprint, render_template

home_blueprint = Blueprint(
    "home", __name__, static_folder="static", template_folder="templates"
)


@home_blueprint.route("/")
def index() -> str:
    """Render the home page."""
    return render_template("index.html.jinja")
