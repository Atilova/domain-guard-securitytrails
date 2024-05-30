from flask import Blueprint
from flask_restx import Api

from integration.api.controllers.account_v1 import ns as securitytrails_account_v1


blueprint = Blueprint('account_api', __name__, url_prefix='/v1/securitytrails')

authorizations = {
    'api_key': {
        'type': 'apiKey',
        'name': 'X-API-Key',
        'in': 'header',
        'description': 'Provide your API key in the X-API-Key header.'
    }
}

api = Api(blueprint,
    doc='/doc/',
    title='SecurityTrails Accounts Operation Api',
    version='1.0',
    security='api_key',
    authorizations=authorizations
)

api.add_namespace(securitytrails_account_v1)