from datetime import timedelta

from dataclasses import dataclass

from typing import Callable, Any, TypeVar

from .base import ValueObject

from domain.Enums.orchestrator import ProcessStatus


OnDoneCallback = TypeVar('OnDoneCallback')
ProcessExecutable = Callable[[], Any]
ProcessOnDoneCallback = Callable[[OnDoneCallback], None]


@dataclass(frozen=True)
class OrchestratorProcessId(ValueObject[str]):
    _value: str


@dataclass(frozen=True)
class OrchestratorExecutable(ValueObject[ProcessExecutable]):
    _value: ProcessExecutable


@dataclass(frozen=True)
class OrchestratorOnDoneCallback(ValueObject[ProcessOnDoneCallback]):
    _value: ProcessOnDoneCallback


@dataclass(frozen=True)
class OrchestratorProcessPid(ValueObject[int]):
    _value: int


@dataclass(frozen=True)
class OrchestratorProcessStatus(ValueObject[ProcessStatus]):
    _value: ProcessStatus


# Todo: add TypeVar and generic here
@dataclass(frozen=True)
class OrchestratorProcessResult(ValueObject[Any]):
    _value: Any


@dataclass(frozen=True)
class OrchestratorProcessException(ValueObject[Exception]):
    _value: Exception


@dataclass(frozen=True)
class OrchestratorProcessElapsedTime(ValueObject[timedelta]):
    _value: timedelta