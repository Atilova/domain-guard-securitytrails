from typing import Protocol, ContextManager, runtime_checkable

from application.UseCases.GetApiKey import GetApiKey
from application.UseCases.NewApiKey import NewApiKey


@runtime_checkable
class IInteractorFactory(Protocol):
    """IInteractorFactory"""

    def fabricate_api_key(self) -> ContextManager[NewApiKey]:
        pass

    def retrieve_api_key(self) -> ContextManager[GetApiKey]:
        pass