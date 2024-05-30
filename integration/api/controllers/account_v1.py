from flask import request
from injector import inject
from http import HTTPStatus
from flask_restx import Resource, abort

from config import conf

from integration.adapters.IInteractorFactory import IInteractorFactory
from integration.api.controllers import securitytrails_account_v1 as ns
from integration.api.models.response.account_v1 import api_key_response_model
from integration.api.extensions.api_key_required import api_key_required

from application.Dto.api_key import (
    GetApiKeyInputDTO,
    NewApiKeyInputDTO,
    ApiKeyCreationStatus
)


require_api_key = api_key_required(conf.api.api_key)

@ns.route('/fabricate')
class FabricateApiKey(Resource):
    """FabricateApiKey"""

    @inject
    def __init__(self, ioc: IInteractorFactory, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__ioc = ioc

    @ns.doc('Fabricate new ApiKey.', security='api_key')
    @ns.marshal_with(api_key_response_model)
    @ns.response(HTTPStatus.CREATED, 'APIKey associated operation initialized successfully.')
    @ns.response(HTTPStatus.FORBIDDEN, 'Maximum active operations associated with APIKey reached.')
    @require_api_key
    def post(self):
        with self.__ioc.fabricate_api_key() as fabricate_api_key:
            output_dto = fabricate_api_key(NewApiKeyInputDTO())

        if output_dto.status is ApiKeyCreationStatus.FORBIDDEN:
            return abort(HTTPStatus.FORBIDDEN)
        return output_dto.to_dict(), HTTPStatus.CREATED

@ns.route('/retrieve/<string:id>')
class RetrieveApiKey(Resource):
    """RetrieveApiKey"""

    @inject
    def __init__(self, ioc: IInteractorFactory, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__ioc = ioc

    @ns.doc('Retrieve fabricated ApiKey.', security='api_key')
    @ns.marshal_with(api_key_response_model)
    @ns.response(HTTPStatus.OK, 'Returned current operation fabrication status associated with ApiKey.')
    @ns.response(HTTPStatus.NOT_FOUND, 'Operation with given ID associated with ApiKey was not found.')
    @require_api_key
    def get(self, id: str):
        with self.__ioc.retrieve_api_key() as retrieve_api_key:
            output_dto = retrieve_api_key(GetApiKeyInputDTO(
                id=id
            ))

        if output_dto.status is ApiKeyCreationStatus.NOT_FOUND:
            return abort(HTTPStatus.NOT_FOUND)
        return output_dto.to_dict(), HTTPStatus.OK

