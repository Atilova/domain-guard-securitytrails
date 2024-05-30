from flask import Flask


def configure_app(app: Flask):
    """configure_app"""

    app.config['RESTX_MASK_SWAGGER'] = False
