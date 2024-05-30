from domain.Entities.mail import Mailbox, MailboxInboxInfo, MailboxInbox
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


class MailboxService:
    """MailboxService"""

    def new_mailbox(self, *, name: EmailName, first_name: EmailFirstname,
                    last_name: EmailLastname, company: EmailCompany) -> Mailbox:

        return Mailbox(
            name=name,
            first_name=first_name,
            last_name=last_name,
            company=company
        )

    def create_inbox_info(self, *, id: InboxId, sender: InboxSender, subject: InboxSubject) -> MailboxInboxInfo:
        return MailboxInboxInfo(
            id=id,
            sender=sender,
            subject=subject
        )
    
    def create_inbox(self, *, info: MailboxInboxInfo, body: InboxBody) -> MailboxInbox:
        return MailboxInbox(
            info=info,
            body=body
        )
