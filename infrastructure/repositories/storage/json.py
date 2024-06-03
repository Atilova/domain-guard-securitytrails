from redis import StrictRedis

from json import loads, dumps, JSONDecodeError

from typing import Protocol, Optional, Callable

from .errors import StorageCRUDError

from domain.Entities.storage import JsonStorageRecord
from domain.ValueObjects.storage import JsonStorageRecordKey, JsonStorageRecordData


def _add_prefix(prefix) -> Callable[[JsonStorageRecordKey], str]:
    """_add_prefix"""

    return lambda key: f'{prefix}:{key.raw()}'


class IStorageService(Protocol):
    """IStorageService"""

    def new_json_record(self, *, key: JsonStorageRecordKey, data: JsonStorageRecordData) -> JsonStorageRecord:
        pass

# Todo: try using generics
class JsonStorageRepository:
    """JsonStorageRepository"""

    def __init__(self, prefix: str, service: IStorageService, client: StrictRedis, data_key: str='data'):
        self.__add_prefix = _add_prefix(prefix)
        self.__service = service
        self.__client = client
        self.__key = data_key

    def insert(self, key: JsonStorageRecordKey, data: JsonStorageRecordData,
               ttl: Optional[int]=None) -> JsonStorageRecord:

        record_key = self.__add_prefix(key)

        try:
            jsonified = dumps(data.raw())
            self.__client.hset(record_key, key=self.__key, value=jsonified)
        except TypeError as exp:
            raise StorageCRUDError(f'Storage insert() failed to dump data for "{record_key}" key.') from exp
        except Exception as exp:
            raise StorageCRUDError(f'Storage failed to insert to "{record_key}" key.') from exp

        if isinstance(ttl, int): self.set_expire(key, ttl)

        return self.__service.new_json_record(key=key, data=data)

    def retrieve(self, key: JsonStorageRecordKey) -> Optional[JsonStorageRecord]:
        if not self.exists(key): return

        record_key = self.__add_prefix(key)
        try:
            data = self.__client.hget(record_key, key=self.__key)
            processed = loads(data)
        except JSONDecodeError as exp:
            raise StorageCRUDError(f'Storage retrieve() failed to decode for "{record_key}" key.') from exp
        except Exception as exp:
            raise StorageCRUDError(f'Storage failed to retrieve by "{record_key}" key.') from exp

        return self.__service.new_json_record(key=key, data=JsonStorageRecordData(processed))

    def update(self, key: JsonStorageRecordKey, new_data: JsonStorageRecordData,
               ttl: Optional[int]=None) -> Optional[JsonStorageRecord]:

        if not self.exists(key): return

        return self.insert(key, new_data, ttl)

    def delete(self, key: JsonStorageRecordKey) -> bool:
        if not self.exists(key): return False

        record_key = self.__add_prefix(key)
        try:
            deleted = self.__client.delete(record_key)
        except Exception as exp:
            raise StorageCRUDError(f'Storage failed to delete "{record_key}" key.') from exp

        return bool(deleted)

    def exists(self, key: JsonStorageRecordKey) -> bool:
        record_key = self.__add_prefix(key)

        try:
            is_exists = self.__client.hexists(record_key, key=self.__key)
        except Exception as exp:
            raise StorageCRUDError(f'Storage exists() failed for "{record_key}" key.') from exp

        return is_exists

    def set_expire(self, key: JsonStorageRecordKey, ttl: int):
        if not self.exists(key): return

        record_key = self.__add_prefix(key)
        try:
            self.__client.expire(record_key, ttl)
        except Exception as exp:
            raise StorageCRUDError(f'Storage set_ttl() failed for "{record_key}" key.') from exp