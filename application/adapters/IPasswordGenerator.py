from typing import Protocol, Optional

from domain.ValueObjects.password import PasswordStr


class IPasswordGenerator(Protocol):
    """IPasswordGenerator"""

    def alphanumeric(self, length: Optional[int] = None) -> PasswordStr:
        pass

    def all_alphanumeric(self, length: Optional[int] = None) -> PasswordStr:
        pass