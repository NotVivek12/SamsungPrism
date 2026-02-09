import functools
import logging
from flask import jsonify, has_app_context

def handle_exceptions(func):
    """
    A decorator to handle exceptions in API endpoints.
    Logs the error and returns a JSON response with an error message.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logging.exception(f"Exception in {func.__name__}: {str(e)}")
            # If we're inside a Flask app context, return JSON response; otherwise re-raise for tests/CLI
            if has_app_context():
                return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500
            raise
    return wrapper
