class MailboxUseBeforeInitialization(Exception):
    """MailboxCalledBeforeInitialization"""


class MailboxRequestError(Exception):
    """MailboxRequestError"""


class MailboxParseError(Exception):
    """MailboxParseError"""