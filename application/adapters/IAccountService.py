from typing import Protocol, Optional

from domain.Entities.account import AccountObtainResult
from domain.ValueObjects.app import ApiKey, Password
from domain.ValueObjects.mail import EmailName
from domain.ValueObjects.account import AccountObtainResultCode


class IAccountService(Protocol):
    """IAccountService"""

    def new_result(self, *, code: AccountObtainResultCode, email: EmailName,
                   api_key: Optional[ApiKey], password: Optional[Password]) -> AccountObtainResult:
        pass
