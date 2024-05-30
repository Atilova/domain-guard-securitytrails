from dataclasses import dataclass

from domain.ValueObjects.storage import JsonStorageRecordKey, JsonStorageRecordData


@dataclass
class JsonStorageRecord:
    key: JsonStorageRecordKey
    data: JsonStorageRecordData