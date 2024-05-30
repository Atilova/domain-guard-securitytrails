from dataclasses import dataclass

from .base import ValueObject

from domain.Enums.account import ObtainResultCode


@dataclass(frozen=True)
class AccountObtainResultCode(ValueObject[ObtainResultCode]):
    _value: ObtainResultCode