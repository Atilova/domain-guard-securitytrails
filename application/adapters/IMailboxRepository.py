from typing import Protocol, Optional

from domain.Entities.mail import Mailbox
from domain.ValueObjects.app import SignUpConfirmationLink


class IMailboxRepository(Protocol):
    """IMailboxRepository"""

    def mailbox(self) -> Optional[Mailbox]:
        pass

    def get_confirmation(self) -> Optional[SignUpConfirmationLink]:
        pass
