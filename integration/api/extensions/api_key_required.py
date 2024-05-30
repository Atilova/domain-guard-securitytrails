import functools
from hmac import compare_digest
from flask import request


def _is_valid(api_key: str, request_api_key: str):
    """Check if the provided API key is valid."""

    return compare_digest(api_key, request_api_key)

def api_key_required(api_key):
    """Decorator to require a valid API key for access."""

    def decorator(func):
        @functools.wraps(func)
        # Todo: find solution how to automatically add 401 response status to swagger-ui
        def wrapper(*args, **kwargs):
            request_api_key = request.headers.get('X-API-Key')
            if request_api_key is None:
                return {'error': 'Please provide an API key in the X-API-Key header.'}, 401

            if not _is_valid(api_key, request_api_key):
                return {'error': 'Invalid API key.'}, 401

            return func(*args, **kwargs)

        return wrapper
    return decorator