from typing import Protocol, Callable


class ISecurityTrailsAccountService(Protocol):
    """ISecurityTrailsService"""

    def obtain_account(self) -> Callable:
        pass

