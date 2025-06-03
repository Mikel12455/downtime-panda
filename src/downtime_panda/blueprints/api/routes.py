from flask import Blueprint

api_blueprint = Blueprint("api", __name__, url_prefix="/api")


@api_blueprint.get("/heartbeat")
def heartbeat():
    """
    Endpoint to check if the API is running.
    """
    return {"status": "ok"}
