from dataclasses import dataclass

from typing import TypeVar

from .base import ValueObject


JsonSerializable = TypeVar('JsonSerializable', int, float, str, list, dict, bool, None)


@dataclass(frozen=True)
class JsonStorageRecordKey(ValueObject[str]):
    _value: str


@dataclass(frozen=True)
class JsonStorageRecordData(ValueObject[JsonSerializable]):
    _value: JsonSerializable
