from typing import Optional

from integration.gateway.consumers.events import ProducerEvents
from integration.gateway.adapters.IGatewayProducer import IGatewayProducer

from application.adapters.IJsonStorageRepository import IJsonStorageRepository
from application.Dto.api_key import ApiKeyOutputDTO

from domain.ValueObjects.storage import JsonStorageRecordKey, JsonStorageRecordData


# Todo: Think of a better way for data manipulation
# Todo: Consider using GatewayApiKeyNotifierState
# Todo: Consider creating response model for rabbitmq

class GatewayApiKeyNotifier:
    """GatewayApiKeyNotifier"""

    def __init__(self, *,
        producer: IGatewayProducer,
        request_storage: IJsonStorageRepository,
        response_storage: IJsonStorageRepository
    ):
        self.__producer = producer
        self.__request_storage = request_storage
        self.__response_storage = response_storage

    def success(self, dto: ApiKeyOutputDTO):
        request_id = self.__retrieve_by_dto(dto)
        if request_id is None: return

        self.notify(request_id, dto)
        self.__remove_by_dto(dto)

    def fail(self, dto: ApiKeyOutputDTO):
        request_id = self.__retrieve_by_dto(dto)
        if request_id is None: return

        self.notify(request_id, dto)
        self.__remove_by_dto(dto)

    def notify(self, _id: str, dto: ApiKeyOutputDTO):
        self.__producer.produce_json({
            'event': ProducerEvents.ACCOUNT_RESPONSE,
            'data': dto.to_dict(),
            '_id': _id
        })

    def register(self, _id: str, dto: ApiKeyOutputDTO):
        self.__request_storage.insert(JsonStorageRecordKey(_id), JsonStorageRecordData(dto.id), 1800)
        self.__response_storage.insert(JsonStorageRecordKey(dto.id), JsonStorageRecordData(_id), 1800)

    def retrieve_by_id(self, _id: str) -> Optional[str]:
        record = self.__request_storage.retrieve(JsonStorageRecordKey(_id))
        if record is None: return

        return record.data.raw()

    def __retrieve_by_dto(self, dto: ApiKeyOutputDTO) -> Optional[str]:
        record = self.__response_storage.retrieve(JsonStorageRecordKey(dto.id))
        if record is None: return

        return record.data.raw()

    def __remove_by_dto(self, dto: ApiKeyOutputDTO):
        request_id = self.__retrieve_by_dto(dto)
        if request_id is None: return

        dto_id_key = JsonStorageRecordKey(dto.id)
        request_id_key = JsonStorageRecordKey(request_id)

        self.__request_storage.delete(request_id_key)
        self.__response_storage.delete(dto_id_key)