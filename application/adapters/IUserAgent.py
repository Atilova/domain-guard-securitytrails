from typing import Protocol

from domain.ValueObjects.user_agent import UserAgentStr


class IUserAgent(Protocol):
    """IUserAgent"""

    def random(self) -> UserAgentStr:
        pass
