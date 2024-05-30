
from datetime import timedelta
from json import dumps, loads, JSONDecodeError

from typing import Protocol, Optional, TypedDict
from dataclasses import dataclass, asdict


class ApiKeyCreationStatus:
    """ApiKeyCreationStatus"""

    NOT_FOUND = 'not_found'
    FORBIDDEN = 'forbidden'
    PROCESSING = 'processing'
    REJECTED = 'rejected'
    READY = 'ready'


class ApiKeyCredentials(TypedDict):
    """ApiKeyCredentials"""

    email: str
    password: str
    api_key: str


class ApiKeyCreationError(TypedDict):
    """ApiKeyCreationError"""

    details: str
    code: int


@dataclass(frozen=True)
class ApiKeyOutputDTO:
    """NewApiKeyOutputDTO"""

    status: ApiKeyCreationStatus
    id: Optional[str] = None
    data: Optional[ApiKeyCredentials] = None
    error: Optional[ApiKeyCreationError] = None
    elapsed: Optional[timedelta] = None

    def to_json(self):
        representation = self.to_dict()
        return dumps(representation, default=str, ensure_ascii=False)

    def to_dict(self):
        representation = asdict(self)
        if self.elapsed is not None:
            representation['elapsed'] = self.elapsed.total_seconds()
        return representation

    @classmethod
    def from_json(cls, json_str: str):
        try:
            decoded = loads(json_str)

            status = decoded['status']
            id = decoded.get('id')
            data = decoded.get('data')
            error = decoded.get('error')
            elapsed_int = decoded.get('elapsed')
            elapsed = elapsed_int if elapsed_int is None else timedelta(seconds=elapsed_int)

            return cls(status=status, id=id, data=data,
                       error=error, elapsed=elapsed)
        except (JSONDecodeError, KeyError):
            return


class IApiKeyNotifier(Protocol):
    """IApiKeyNotifier"""

    def success(self, dto: ApiKeyOutputDTO):
        ...

    def fail(self, dto: ApiKeyOutputDTO):
        ...


@dataclass(frozen=True)
class NewApiKeyInputDTO:
    """NewApiKeyInputDTO"""

    notifier: Optional[IApiKeyNotifier]=None


@dataclass(frozen=True)
class GetApiKeyInputDTO:
    """GetApiKeyInputDTO"""

    id: str