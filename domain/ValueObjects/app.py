from dataclasses import dataclass

from .base import ValueObject


@dataclass(frozen=True)
class SignUpConfirmationLink(ValueObject[str]):
    _value: str


@dataclass(frozen=True)
class Password(ValueObject[str]):
    _value: str


@dataclass(frozen=True)
class ApiKey(ValueObject[str]):
    _value: str