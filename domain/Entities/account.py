from dataclasses import dataclass

from typing import Optional

from domain.ValueObjects.app import ApiKey, Password
from domain.ValueObjects.mail import EmailName
from domain.ValueObjects.account import AccountObtainResultCode


@dataclass
class AccountObtainResult:
    code: AccountObtainResultCode
    email: EmailName
    api_key: Optional[ApiKey] = None
    password: Optional[Password] = None