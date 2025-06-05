from flask import Blueprint

error_blueprint = Blueprint("errors", __name__, url_prefix="/errors")


@error_blueprint.app_errorhandler(404)
def not_found_error(error):
    """
    Handle 404 Not Found errors.
    """
    return {"error": "Not Found"}, 404


@error_blueprint.app_errorhandler(500)
def internal_server_error(error):
    """
    Handle 500 Internal Server Error.
    """
    return {"error": "Internal Server Error"}, 500


@error_blueprint.app_errorhandler(403)
def forbidden_error(error):
    """
    Handle 403 Forbidden errors.
    """
    return {"error": "Forbidden"}, 403
