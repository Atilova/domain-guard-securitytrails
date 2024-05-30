from dataclasses import dataclass

from .base import ValueObject


@dataclass(frozen=True)
class EmailName(ValueObject[str]):
    _value: str


@dataclass(frozen=True)
class EmailFirstname(ValueObject[str]):
    _value: str


@dataclass(frozen=True)
class EmailLastname(ValueObject[str]):
    _value: str


@dataclass(frozen=True)
class EmailCompany(ValueObject[str]):
    _value: str


@dataclass(frozen=True)
class InboxId(ValueObject[int]):
    _value: int


@dataclass(frozen=True)
class InboxSender(ValueObject[str]):
    _value: str


@dataclass(frozen=True)
class InboxSubject(ValueObject[str]):
    _value: str


@dataclass(frozen=True)
class InboxBody(ValueObject[str]):
    _value: str