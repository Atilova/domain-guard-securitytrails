from domain.Entities.storage import JsonStorageRecord
from domain.ValueObjects.storage import JsonStorageRecordKey, JsonStorageRecordData


class StorageService:
    """StorageService"""

    def new_json_record(self, *, key: JsonStorageRecordKey, data: JsonStorageRecordData) -> JsonStorageRecord:
        return JsonStorageRecord(key=key, data=data)