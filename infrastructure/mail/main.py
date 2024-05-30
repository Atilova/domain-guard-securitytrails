import re
import requests
from random import choice, randint
from json import loads, JSONDecodeError

from typing import Protocol, Optional

from .errors import (
    MailboxUseBeforeInitialization,
    MailboxRequestError,
    MailboxParseError
)

from domain.Entities.mail import Mailbox, MailboxInboxInfo, MailboxInbox
from domain.ValueObjects.user_agent import UserAgentStr
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


API = {
    'index': 'https://www.minuteinbox.com/index/index',
    'refresh': 'https://www.minuteinbox.com/index/refresh',
    'email': lambda email_id: f'https://www.minuteinbox.com/email/id/{email_id}'
}
DEFAULT_INBOX_ID = 1
INBOX_SENDER_REGEX =  r'<([^<>]+)>'
COMPANY_SUFFIX = ['Solutions','Software Inc.','Technology Inc.','Technologies','Computers','Systems','IT','Connect','Digital','Tech','PC Professionals','Technology Partners','Group','Tech Services','& Co','Labs','PLLC','Tech','Corp.','LLC','LLP','LP','P.C','Incorporated','S.A.S.','GmbH & Co. KG','AG & Co. KG','SE & Co. KGaA']


def _get_headers(*, user_agent: str):
    """get_headers"""

    return {
        'User-Agent': user_agent,
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'en-US;q=0.7,en;q=0.3',
        'X-Requested-With': 'XMLHttpRequest',
        'Connection': 'keep-alive',
        'Referer': 'https://www.minuteinbox.com/'
    }

def _decode_index_response(response: requests.Response):
    """decode_index_response"""

    mailbox = loads(response.content.decode('utf-8-sig')).get('email')
    if mailbox is None:
        raise KeyError

    return mailbox

def _parse_mailbox(mailbox: str):
    """parse_mailbox"""

    return mailbox.split('@')[0].split('.')

def _compose_company_name(first_name: str, last_name: str):
    """compose_company_name"""

    prefix_a = first_name[:2]
    prefix_b = last_name[:randint(2, 5)]
    suffix = _get_company_suffix()

    return f'{prefix_a}{prefix_b} {suffix}'

def _get_company_suffix():
    """get_company_suffix"""

    return choice(COMPANY_SUFFIX)

def _decode_refresh_response(response: requests.Response):
    """decode_refresh_response"""

    return loads(response.content.decode('utf-8-sig'))

def _is_default_inbox(inbox: dict):
    """is_default_inbox"""

    inbox_id = inbox.get('id')
    return inbox_id is None or inbox_id == DEFAULT_INBOX_ID

def _parse_inbox(inbox: dict):
    """parse_inbox"""

    _id = inbox['id']
    sender = _get_sender(inbox['od'])
    subject = inbox['predmet']

    return _id, sender, subject

def _get_sender(sender: str):
    """get_sender"""

    is_matched = re.search(INBOX_SENDER_REGEX, sender)
    return is_matched and is_matched.group(1)


class IUserAgent(Protocol):
    """IUserAgent"""

    def random(self) -> UserAgentStr:        
        pass


class IMailboxService(Protocol):
    """IMailboxService"""

    def new_mailbox(self, *, name: EmailName, first_name: EmailFirstname,
               last_name: EmailLastname, company: EmailCompany) -> Mailbox:
        pass

    def create_inbox_info(self, *, id: InboxId, sender: InboxSender, subject: InboxSubject) -> MailboxInboxInfo:
       pass

    def create_inbox(self, *, info: MailboxInboxInfo, body: InboxBody) -> MailboxInbox:
        pass


class TenMinuteMailbox:
    """TenMinuteMailbox"""

    def __init__(self, user_agent: IUserAgent, service: IMailboxService):
        self.__user_agent = user_agent
        self.__service = service
        self.__session = requests.Session()
        self.__cookies = {}
        self.__mailbox: Optional[Mailbox] = None

        ua = self.__user_agent.random().raw()
        self.__headers = _get_headers(user_agent=ua)

    def mailbox(self) -> Mailbox:
        if self.__mailbox is not None:
            return self.__mailbox

        try:
            response = self.__session.get(API['index'], headers=self.__headers)
        except Exception as exp:
            raise MailboxRequestError('Failed to get mailbox() response.', exp) from exp

        try:
            mailbox = _decode_index_response(response)
            first_name, last_name = _parse_mailbox(mailbox)
            company_name = _compose_company_name(first_name, last_name)
        except (JSONDecodeError, KeyError) as exp:
            raise MailboxParseError('Failed to parse mailbox() response.', exp) from exp

        self.__cookies['MI'] = mailbox

        self.__mailbox = self.__service.new_mailbox(
            name=EmailName(mailbox),
            first_name=EmailFirstname(first_name.capitalize()),
            last_name=EmailLastname(last_name.capitalize()),
            company=EmailCompany(company_name)
        )

        return self.__mailbox

    def inbox_list(self) -> list[Optional[MailboxInboxInfo]]:
        if self.__mailbox is None:
            raise MailboxUseBeforeInitialization('inbox_list() used before initialization.')

        # Todo: implement in future


    def __inbox_by_id(self, info: MailboxInboxInfo) -> Optional[MailboxInbox]:
        if self.__mailbox is None:
            raise MailboxUseBeforeInitialization('inbox_by_id() used before initialization.')

        # Todo: make public in future

        inbox_id = info.id.raw()
        try:
            body = self.__session.get(API['email'](inbox_id), headers=self.__headers,
                                        cookies=self.__cookies).text
        except Exception as exp:
          raise MailboxRequestError('Failed to get inbox_by_id() response.', exp) from exp

        return self.__service.create_inbox(
            info=info,
            body=InboxBody(body)
        )

    def latest(self) -> Optional[MailboxInbox]:
        if self.__mailbox is None:
            raise MailboxUseBeforeInitialization('latest() used before initialization.')

        # Todo: add cache & cooldown in future
        try:
            response = self.__session.get(API['refresh'], headers=self.__headers,
                                          cookies=self.__cookies)
        except Exception as exp:
            raise MailboxRequestError('Failed to get latest() response', exp) from exp

        try:
            inbox_list = _decode_refresh_response(response)
            latest, *_ = inbox_list

            if _is_default_inbox(latest):
                return

            inbox_id, inbox_sender, inbox_subject  = _parse_inbox(latest)
        except (JSONDecodeError, KeyError) as exp:
            raise MailboxParseError('Failed to parse latest() response.', exp) from exp

        latest_info = self.__service.create_inbox_info(
            id=InboxId(inbox_id),
            sender=InboxSender(inbox_sender),
            subject=InboxSubject(inbox_subject)
        )

        inbox = self.__inbox_by_id(latest_info)

        return inbox