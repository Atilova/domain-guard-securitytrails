from application.adapters.Interactor import Interactor
from application.adapters.IOrchestrator import IOrchestrator
from application.adapters.IJsonStorageRepository import IJsonStorageRepository

from application.Dto.mappers.api_key import map_get_api_key_to_dto
from application.Dto.api_key import GetApiKeyInputDTO, ApiKeyOutputDTO

from domain.ValueObjects.storage import JsonStorageRecordKey, JsonStorageRecordData


class GetApiKey(Interactor[GetApiKeyInputDTO, ApiKeyOutputDTO]):
    def __init__(self,
        orchestrator: IOrchestrator,
        storage: IJsonStorageRepository,
    ):
        self.__orchestrator = orchestrator
        self.__storage = storage

    def __call__(self, data: GetApiKeyInputDTO) -> ApiKeyOutputDTO:
        # Todo: potentially try updating state from orchestrator
        job = self.__storage.retrieve(JsonStorageRecordKey(data.id))
        output_dto = map_get_api_key_to_dto(job)

        return output_dto