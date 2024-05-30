from dataclasses import dataclass

from .base import ValueObject


@dataclass(frozen=True)
class PasswordStr(ValueObject[str]):
    _value: str