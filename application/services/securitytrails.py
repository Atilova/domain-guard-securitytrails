import logging
from seleniumbase import SB

from threading import Lock
from functools import partial

from enum import Enum, auto
from dataclasses import dataclass

from typing import Optional, Callable
from contextlib import _GeneratorContextManager

from utils.rsleep import rsleep
from utils.notnone import notnone_init

from application.adapters.IMailboxRepository import IMailboxRepository
from application.adapters.ISignUpWebDriverService import ISignUpWebDriverService
from application.adapters.WebDriverFactory import WebDriverFactory
from application.adapters.IAccountService import IAccountService
from application.adapters.IUserAgent import IUserAgent
from application.adapters.IPasswordGenerator import IPasswordGenerator

from domain.Entities.account import AccountObtainResult
from domain.Enums.account import ObtainResultCode
from domain.ValueObjects.app import Password, SignUpConfirmationLink, ApiKey
from domain.ValueObjects.mail import EmailName
from domain.ValueObjects.account import AccountObtainResultCode

from infrastructure.services.webdriver.errors import (
	WebDriverCaptchaError,
	WebDriverElementMissingError,
	WebDriverServerError
)


logger = logging.getLogger('SecurityTrailsAccountService')

MAX_FAILED_TIMES = 6
PASSWORD_LENGTH = 24


class ObtainState(Enum):
    INIT = auto()
    OPEN_BROWSER = auto()
    FILL_FORM = auto()
    SUBMIT_FORM = auto()
    GET_CONFIRMATION = auto()
    CONFIRM_SIGN_UP = auto()
    GET_CREDENTIALS = auto()
    QUIT = auto()
    DONE = auto()


@dataclass
class TempState:
    """TempState"""

    state: ObtainState
    code: ObtainResultCode
    email: EmailName
    failed_times: int
    driver: Optional[SB] = None
    ctx: Optional[_GeneratorContextManager] = None
    webdriver: Optional[ISignUpWebDriverService] = None
    password: Optional[Password] = None
    link: Optional[SignUpConfirmationLink] = None
    api_key: Optional[ApiKey] = None


def _is_state(current: ObtainState, compared: ObtainState) -> bool:
    """_is_state"""

    return current == compared

def _clean_up_driver(ctx: _GeneratorContextManager):
    """_clean_up_driver"""

    try:
        ctx.__exit__(None, None, None)
    except Exception as exp:
        logger.exception('Failed to quit driver.')

def _map_result(temp: TempState, service: IAccountService) -> AccountObtainResult:
    """_map_result"""

    return service.new_result(
        code=AccountObtainResultCode(temp.code),
        email=temp.email,
        api_key=temp.api_key,
        password=temp.password
    )

def _obtain(*,
    mailbox_repository: IMailboxRepository,
    webdriver_factory: WebDriverFactory,
    service: IAccountService,
    user_agent: IUserAgent,
    password_generator: IPasswordGenerator,
    lock: Lock,
    driver_params: dict
):
    """_obtain"""

    mailbox = mailbox_repository.mailbox()
    temp = TempState(state=ObtainState.INIT, code=ObtainResultCode.UNDEFINED,
                     email=mailbox.name, failed_times=0)
    params = {
        'uc': True,
        'browser': 'chrome',
        'headless': False
    }
    params |= driver_params

    while not _is_state(temp.state, ObtainState.DONE):
        if temp.failed_times > MAX_FAILED_TIMES:
            temp.code = ObtainResultCode.TIMEOUTED
            temp.state = ObtainState.QUIT

        try:
            match temp.state:
                case ObtainState.INIT:
                    with lock:
                        temp.ctx = SB(**params, agent=user_agent.random().raw())
                        temp.driver = temp.ctx.__enter__()
                    temp.webdriver = webdriver_factory(temp.driver)
                    temp.state = ObtainState.OPEN_BROWSER
                    logger.debug('Initialization complete.')
                case ObtainState.OPEN_BROWSER:
                    try:
                        temp.webdriver.open()
                        temp.state = ObtainState.FILL_FORM
                        logger.debug('Browser opened successfully.')
                    except WebDriverElementMissingError:
                        temp.code = ObtainResultCode.FAILED
                        temp.state = ObtainState.QUIT
                        logger.debug('Failed to open browser. Quitting.')
                case ObtainState.FILL_FORM:
                    password = Password(password_generator.alphanumeric(PASSWORD_LENGTH).raw())
                    temp.password = password
                    temp.webdriver.fill_form(
                        email=mailbox.name,
                        first_name=mailbox.first_name,
                        password=password
                    )
                    temp.state = ObtainState.SUBMIT_FORM
                    logger.debug('Form filled successfully.')
                    rsleep(2, 3)
                case ObtainState.SUBMIT_FORM:
                    try:
                        temp.webdriver.submit_form()
                        temp.state = ObtainState.GET_CONFIRMATION
                        temp.failed_times = 0
                        logger.debug('Account created successfully.')
                    except WebDriverServerError:
                        temp.failed_times += 1.5
                        _clean_up_driver(temp.ctx)
                        temp.state = ObtainState.INIT
                        # Todo: add email already exists verification.
                        logger.debug('Server error encountered during form submission.')
                    except WebDriverCaptchaError:
                        temp.failed_times += 1
                        logger.debug('Captcha encountered during form submission.')
                        rsleep(10, 15)
                case ObtainState.GET_CONFIRMATION:
                    temp.failed_times += 0.2
                    link = mailbox_repository.get_confirmation()
                    if link is not None:
                        temp.failed_times = 0
                        logger.debug('Confirmation link obtained: %s', link.raw())
                        temp.link = link
                        temp.state = ObtainState.CONFIRM_SIGN_UP
                        continue
                    logger.debug('No confirmation link available. Proceeding to next loop.')
                    rsleep(2, 2)
                case ObtainState.CONFIRM_SIGN_UP:
                    temp.webdriver.confirm_sign_up(link)
                    temp.state = ObtainState.GET_CREDENTIALS
                    logger.debug('Sign-up confirmed.')
                case ObtainState.GET_CREDENTIALS:
                    try:
                        api_key = temp.webdriver.get_credentials()
                        temp.api_key = api_key
                        temp.code = ObtainResultCode.SUCCESS
                        temp.state = ObtainState.QUIT
                        logger.debug('API key obtained: %s', api_key.raw())
                    except WebDriverElementMissingError:
                        temp.failed_times += 1
                        logger.debug('Missing element encountered while retrieving credentials.')
                        rsleep(2, 2)
                case ObtainState.QUIT:
                    _clean_up_driver(temp.ctx)
                    temp.state = ObtainState.DONE
                    logger.debug('Quitting.')
                case _:
                    logger.error('Unknown state encountered. Quitting.')
                    temp.code = ObtainResultCode.FAILED
                    temp.state = ObtainState.QUIT
        except Exception as exp:
            logger.exception('Uncaught exception encountered. Quitting.')
            temp.code = ObtainResultCode.FAILED
            temp.state = ObtainState.QUIT

    mapped = _map_result(temp, service)
    return mapped


class SecurityTrailsAccountService:
    """SecurityTrailsService"""

    def __init__(self, *,
        mailbox_repository: IMailboxRepository,
        webdriver_factory: WebDriverFactory,
        account_service: IAccountService,
        user_agent: IUserAgent,
        password_generator: IPasswordGenerator,
        lock: Lock,
        driver_params
    ):
        self.__mailbox_repository = mailbox_repository
        self.__webdriver_factory = webdriver_factory
        self.__account_service = account_service
        self.__user_agent = user_agent
        self.__password_generator = password_generator
        self.__driver_params = driver_params

        # Insure proper Lock from multiprocessing is passed
        # Use multiprocessing.Manager.Lock for Pool
        # Do not use multiprocessing.Lock for Pool - not pickle serializable
        self.__lock = lock

    def obtain_account(self) -> Callable:
        call = partial(_obtain,
            mailbox_repository=self.__mailbox_repository,
            webdriver_factory=self.__webdriver_factory,
            service=self.__account_service,
            user_agent=self.__user_agent,
            password_generator=self.__password_generator,
            lock=self.__lock,
            driver_params=self.__driver_params
        )

        return call()