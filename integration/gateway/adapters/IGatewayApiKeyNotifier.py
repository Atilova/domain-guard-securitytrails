from typing import Protocol, Optional

from application.Dto.api_key import ApiKeyOutputDTO


class IGatewayApiKeyNotifier(Protocol):
    def success(self, dto: ApiKeyOutputDTO):
        pass

    def fail(self, dto: ApiKeyOutputDTO):
        pass

    def notify(self, _id: str, dto: ApiKeyOutputDTO):
        pass

    def register(self, _id: str, dto: ApiKeyOutputDTO):
        pass

    def retrieve_by_id(self, _id: str) -> Optional[str]:
        pass

