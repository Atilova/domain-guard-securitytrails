from seleniumbase import SB

from config import conf

from multiprocessing import Manager
from contextlib import contextmanager

from typing import Iterator

from application.adapters.IOrchestrator import IOrchestrator
from application.adapters.IJsonStorageRepository import IJsonStorageRepository
from application.UseCases.GetApiKey import GetApiKey
from application.UseCases.NewApiKey import NewApiKey
from application.services.securitytrails import SecurityTrailsAccountService

from domain.Services.mail import MailboxService
from domain.Services.account import AccountService

from infrastructure.mail.main import TenMinuteMailbox
from infrastructure.user_agent.main import UserAgent
from infrastructure.password.main import PasswordGenerator
from infrastructure.repositories.mail.securitytrails import MailboxRepository
from infrastructure.services.webdriver.securitytrails import SignupWebDriverService
from infrastructure.config import DriverConfig


def _compose_driver_params(config: DriverConfig):
    """_compose_driver_params"""

    return {
        'headless': config.is_headless
    }

def _new_mailbox_repository(*, user_agent, mailbox_service):
    """_new_mailbox_repository"""

    mailbox_provider = TenMinuteMailbox(user_agent=user_agent, service=mailbox_service)
    return MailboxRepository(mailbox_provider)

def _sign_up_webdriver_factory(driver: SB) -> SignupWebDriverService:
    """_sign_up_webdriver_factory"""
    return SignupWebDriverService(driver)

def _new_account_service(*, mailbox_repository, account_service, user_agent, password_generator, lock, params):
    """_new_account_service"""

    return SecurityTrailsAccountService(
		mailbox_repository=mailbox_repository,
		webdriver_factory=_sign_up_webdriver_factory,
		account_service=account_service,
		user_agent=user_agent,
		password_generator=password_generator,
		lock=lock,
		driver_params=params
	)


class InteractorFactory:
    """InteractorFactory"""

    def __init__(self,
        orchestrator: IOrchestrator,
        storage: IJsonStorageRepository
    ):
        self.__orchestrator = orchestrator
        self.__storage = storage
        self.__mailbox_service = MailboxService()
        self.__account_service = AccountService()
        self.__user_agent = UserAgent()
        self.__password_generator = PasswordGenerator()
        self.__manager = Manager()
        self.__lock = self.__manager.Lock()
        self._driver_params = _compose_driver_params(conf.driver)

    @contextmanager
    def fabricate_api_key(self) -> Iterator[NewApiKey]:
        yield NewApiKey(
            orchestrator=self.__orchestrator,
            storage=self.__storage,
            service=_new_account_service(
                mailbox_repository=_new_mailbox_repository(
                    user_agent=self.__user_agent,
                    mailbox_service=self.__mailbox_service
                ),
                account_service=self.__account_service,
                user_agent=self.__user_agent,
                password_generator=self.__password_generator,
                lock=self.__lock,
                params=self._driver_params
            )
        )

    @contextmanager
    def retrieve_api_key(self) -> Iterator[GetApiKey]:
         yield GetApiKey(
            orchestrator=self.__orchestrator,
            storage=self.__storage
        )