from bs4 import BeautifulSoup

from typing import Protocol, Optional

from domain.Entities.mail import Mailbox, MailboxInboxInfo, MailboxInbox
from domain.ValueObjects.mail import InboxBody
from domain.ValueObjects.app import SignUpConfirmationLink

from infrastructure.mail.errors import (
    MailboxUseBeforeInitialization,
    MailboxRequestError,
    MailboxParseError
)


SECURITYTRAILS_MAIL = 'hello@securitytrails.com'
CONFIRM_EMAIL_SELECTOR = {
    'name': 'a',
    'string': 'Confirm email address'
}

def _is_securitytrails_sender(info: MailboxInboxInfo):
    """is_securitytrails_sender"""

    return info.sender.raw() == SECURITYTRAILS_MAIL

def _is_securitytrails_inbox(inbox: Optional[MailboxInbox]):
    """is_securitytrails_inbox"""

    return inbox is not None and _is_securitytrails_sender(inbox.info)

def _extract_link(body: InboxBody):
    """extract_link"""

    soup = BeautifulSoup(body.raw(), 'html.parser')
    link = soup.find(**CONFIRM_EMAIL_SELECTOR)

    return link if link is None else link.get('href')


class IMailboxProvider(Protocol):
    """IMailboxProvider"""

    def mailbox(self) -> Mailbox:
        pass

    def inbox_list(self) -> list[Optional[MailboxInboxInfo]]:
        # Todo: implement in future
        pass

    def latest(self) -> Optional[MailboxInbox]:
        pass


class MailboxRepository:
    """MailboxRepository"""

    def __init__(self, provider: IMailboxProvider):
        self.__provider = provider

    def mailbox(self) -> Optional[Mailbox]:
        try:
            return self.__provider.mailbox()
        except (MailboxRequestError, MailboxParseError) as exp:
            # Todo: add logging
            return

    def get_confirmation(self) -> Optional[SignUpConfirmationLink]:
        try:
            inbox = self.__provider.latest()
            if not _is_securitytrails_inbox(inbox):
                return
        except (MailboxUseBeforeInitialization) as exp:
            # Todo: add logging
            return
        except (MailboxRequestError, MailboxParseError) as exp:
            # Todo: add logging
            return

        link = _extract_link(inbox.body)
        return link if link is None else SignUpConfirmationLink(link)