from flask_restx import fields
from integration.api.controllers import securitytrails_account_v1 as ns


api_key_response_model = ns.model('ApiKeyFabrication', {
    'status': fields.String(required=True, description='Status of the user'),
    'id': fields.String(required=True, description='ID of the user'),
    'data': fields.Nested(ns.model('AccountApiKey', {
        'email': fields.String(required=True, description='Email of the user'),
        'password': fields.String(required=True, description='Password of the user'),
        'api_key': fields.String(required=True, description='API Key of the user'),
    }), description='User data'),
    'error': fields.String(description='Error message, if any'),
    'elapsed': fields.Float(description='Elapsed time for the request'),
})