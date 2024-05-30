from dataclasses import dataclass

from .base import ValueObject


@dataclass(frozen=True)
class UserAgentStr(ValueObject[str]):
    _value: str
