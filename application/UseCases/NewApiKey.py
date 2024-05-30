from typing import Optional

from application.adapters.Interactor import Interactor
from application.adapters.IOrchestrator import IOrchestrator
from application.adapters.IJsonStorageRepository import IJsonStorageRepository
from application.adapters.ISecurityTrailsAccountService import ISecurityTrailsAccountService
from application.Dto.mappers.api_key import map_new_api_key_to_dto
from application.Dto.api_key import (
    NewApiKeyInputDTO,
    ApiKeyOutputDTO,
    ApiKeyCreationStatus
)

from domain.Entities.orchestrator import OrchestratorResult
from domain.ValueObjects.storage import JsonStorageRecordKey, JsonStorageRecordData
from domain.ValueObjects.orchestrator import OrchestratorExecutable, OrchestratorOnDoneCallback


class NewApiKey(Interactor[NewApiKeyInputDTO, ApiKeyOutputDTO]):
    def __init__(self,
        orchestrator: IOrchestrator,
        storage: IJsonStorageRepository,
        service: ISecurityTrailsAccountService
    ):
        self.__orchestrator = orchestrator
        self.__storage = storage
        self.__service = service

    def __call__(self, data: NewApiKeyInputDTO) -> ApiKeyOutputDTO:
        if not self.__orchestrator.is_allowed():
            return ApiKeyOutputDTO(status=ApiKeyCreationStatus.FORBIDDEN)

        self.__notifier = data.notifier

        job_id = self.__orchestrator.put(OrchestratorExecutable(self.__service.obtain_account),
                                         OrchestratorOnDoneCallback(self.__done)).raw()

        output_dto = ApiKeyOutputDTO(id=job_id, status=ApiKeyCreationStatus.PROCESSING)

        self.__storage.insert(JsonStorageRecordKey(output_dto.id),
                              JsonStorageRecordData(output_dto.to_json()), 1800)

        return output_dto

    def __done(self, result: OrchestratorResult):
        job_id = result.id.raw()
        record = self.__storage.retrieve(JsonStorageRecordKey(job_id))

        stored_dto = ApiKeyOutputDTO.from_json(record.data.raw())
        output_dto = map_new_api_key_to_dto(result, stored_dto)

        self.__storage.insert(JsonStorageRecordKey(output_dto.id),
                              JsonStorageRecordData(output_dto.to_json()), 1800)

        if self.__notifier is None: return

        self.__notifier.success(output_dto)