from dataclasses import dataclass

from domain.ValueObjects.mail import (
    EmailName,
    EmailFirstname,
    EmailLastname,
    EmailCompany,
    InboxId,
    InboxSender,
    InboxSubject,
    InboxBody
)


@dataclass
class Mailbox:
    name: EmailName
    first_name: EmailFirstname
    last_name: EmailLastname
    company: EmailCompany


@dataclass
class MailboxInboxInfo:
    id: InboxId
    sender: InboxSender
    subject: InboxSubject


@dataclass
class MailboxInbox:
    info: MailboxInboxInfo
    body: InboxBody
