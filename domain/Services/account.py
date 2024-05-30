from typing import Optional

from domain.Entities.account import AccountObtainResult
from domain.ValueObjects.app import ApiKey, Password
from domain.ValueObjects.mail import EmailName
from domain.ValueObjects.account import AccountObtainResultCode


class AccountService:
    """AccountService"""

    def new_result(self, *, code: AccountObtainResultCode, email: EmailName,
                   api_key: Optional[ApiKey], password: Optional[Password]) -> AccountObtainResult:

        return AccountObtainResult(
            code=code,
            email=email,
            api_key=api_key,
            password=password
        )