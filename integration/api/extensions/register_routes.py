from flask import Flask

from integration.api.views.securitytrails_v1 import blueprint as account_api


def register_routes(app: Flask):
    """register_routes"""

    app.register_blueprint(account_api)