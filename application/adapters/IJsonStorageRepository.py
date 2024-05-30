from typing import Protocol, Optional

from domain.Entities.storage import JsonStorageRecord
from domain.ValueObjects.storage import JsonStorageRecordKey, JsonStorageRecordData


class IJsonStorageRepository(Protocol):
    """IJsonStorageRepository"""

    def insert(self, key: JsonStorageRecordKey, data: JsonStorageRecordData, ttl: Optional[int]) -> JsonStorageRecord:
        pass

    def retrieve(self, key: JsonStorageRecordKey) -> Optional[JsonStorageRecord]:
        pass

    def update(self, key: JsonStorageRecordKey, new_data: JsonStorageRecordData, ttl: Optional[int]) -> Optional[JsonStorageRecord]:
        pass

    def delete(self, key: JsonStorageRecordKey) -> bool:
        pass

    def exists(self, key: JsonStorageRecordKey) -> bool:
        pass

    def set_expire(self, key: JsonStorageRecordKey, ttl: int):
        pass
